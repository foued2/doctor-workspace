from __future__ import annotations

import json
import random
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

from io_manager import IOManager, QueuedWrite

DEFAULT_BATCH_SIZE = 5
MAX_OPERATIONS_PER_BATCH = 10
MAX_RUNTIME_PER_BATCH_SECONDS = 45
MIN_THROTTLE_SECONDS = 0.10
MAX_THROTTLE_SECONDS = 0.25
MAX_FILE_OPERATIONS_PER_BATCH = 10
CPU_SPIKE_THRESHOLD_PERCENT = 85.0
CPU_PAUSE_LIMIT_SECONDS = 5.0
MAX_INJECTION_BATCH_SIZE = 2


class ExecutionControlError(RuntimeError):
    """Base exception for controlled execution failures."""


class OperationLimitExceeded(ExecutionControlError):
    """Raised when a batch exceeds the allowed number of operations."""


class FileOperationLimitExceeded(ExecutionControlError):
    """Raised when a batch exceeds the allowed number of file operations."""


class BatchRuntimeExceeded(ExecutionControlError):
    """Raised when a batch runs past its runtime budget."""


class BatchValidationError(ExecutionControlError):
    """Raised when a batch-level validation gate fails."""


class ResourceSafetyPauseExceeded(ExecutionControlError):
    """Raised when CPU pressure stays high for too long."""


@dataclass
class BatchState:
    name: str
    pipeline: str
    batch_index: int
    started_at: float
    operations: int = 0
    file_operations: int = 0

    @property
    def elapsed_seconds(self) -> float:
        return time.monotonic() - self.started_at


class ResourceSafetyGuard:
    """Pauses execution when system pressure is too high."""

    def __init__(
        self,
        cpu_threshold_percent: float = CPU_SPIKE_THRESHOLD_PERCENT,
        pause_limit_seconds: float = CPU_PAUSE_LIMIT_SECONDS,
    ) -> None:
        self.cpu_threshold_percent = cpu_threshold_percent
        self.pause_limit_seconds = pause_limit_seconds
        self._psutil = None
        try:
            import psutil  # type: ignore
        except ImportError:
            self._psutil = None
        else:
            self._psutil = psutil
            self._psutil.cpu_percent(interval=None)

    def pause_if_needed(self, controller: "ExecutionController") -> None:
        if self._psutil is None:
            return

        pause_started = time.monotonic()
        current_cpu = self._psutil.cpu_percent(interval=0.0)
        while current_cpu >= self.cpu_threshold_percent:
            controller.raise_if_batch_expired()
            if time.monotonic() - pause_started >= self.pause_limit_seconds:
                raise ResourceSafetyPauseExceeded(
                    f"CPU remained above {self.cpu_threshold_percent:.0f}% for "
                    f"{self.pause_limit_seconds:.1f}s; batch aborted."
                )
            time.sleep(controller.next_delay_seconds())
            current_cpu = self._psutil.cpu_percent(interval=0.05)


class BuildPipeline:
    """Owns file creation, conversion, and queued atomic writes."""

    @staticmethod
    def validate_write_batch(pending_writes: Iterable[QueuedWrite]) -> None:
        for write in pending_writes:
            if not write.content:
                raise BatchValidationError(f"Queued write for {write.path} is empty.")
            missing_markers = [
                marker for marker in write.required_markers if marker not in write.content
            ]
            if missing_markers:
                raise BatchValidationError(
                    f"Queued write for {write.path} is missing markers: "
                    f"{', '.join(missing_markers)}"
                )

    def commit_batch(self, controller: "ExecutionController", reason: str = "commit") -> list[Path]:
        pending_writes = controller.io_manager.peek()
        if not pending_writes:
            return []
        current_batch = controller.current_batch
        if current_batch is not None:
            projected_operations = current_batch.operations + len(pending_writes)
            projected_file_operations = current_batch.file_operations + len(pending_writes)
            if projected_operations > controller.max_operations_per_batch:
                raise OperationLimitExceeded(
                    f"Commit '{reason}' would exceed "
                    f"{controller.max_operations_per_batch} operations in batch "
                    f"'{current_batch.name}'."
                )
            if projected_file_operations > controller.max_file_operations_per_batch:
                raise FileOperationLimitExceeded(
                    f"Commit '{reason}' would exceed "
                    f"{controller.max_file_operations_per_batch} file operations in batch "
                    f"'{current_batch.name}'."
                )
        self.validate_write_batch(pending_writes)
        return controller.io_manager.flush()


class ValidationPipeline:
    """Runs validation only at batch boundaries or via explicit requests."""

    def validate_batch(
        self,
        controller: "ExecutionController",
        batch_name: str,
        validator: Callable[[], Any],
    ) -> Any:
        result = controller.run_operation(
            validator,
            label=f"validate:{batch_name}",
            file_operation=False,
        )
        if result is False:
            raise BatchValidationError(f"Validation failed for {batch_name}.")
        return result


class InjectionPipeline:
    """Keeps failure simulation strictly bounded."""

    def process_batch(
        self,
        controller: "ExecutionController",
        items: Iterable[Any],
        injector: Callable[[Any], Any],
        batch_size: int = 1,
        batch_name: str = "injection",
    ) -> list[Any]:
        safe_batch_size = max(1, min(batch_size, MAX_INJECTION_BATCH_SIZE))
        return controller.process_batch(
            items,
            injector,
            batch_size=safe_batch_size,
            pipeline="injection",
            flush_writes=False,
            file_operation=False,
            batch_name=batch_name,
        )


class ExecutionController:
    """Sequential execution harness with bounded batches and queued writes."""

    def __init__(
        self,
        project_root: Path | str,
        *,
        io_manager: Optional[IOManager] = None,
        max_operations_per_batch: int = MAX_OPERATIONS_PER_BATCH,
        max_runtime_per_batch_seconds: int = MAX_RUNTIME_PER_BATCH_SECONDS,
        max_file_operations_per_batch: int = MAX_FILE_OPERATIONS_PER_BATCH,
        min_throttle_seconds: float = MIN_THROTTLE_SECONDS,
        max_throttle_seconds: float = MAX_THROTTLE_SECONDS,
        random_seed: Optional[int] = None,
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.max_operations_per_batch = max_operations_per_batch
        self.max_runtime_per_batch_seconds = max_runtime_per_batch_seconds
        self.max_file_operations_per_batch = max_file_operations_per_batch
        self.min_throttle_seconds = min_throttle_seconds
        self.max_throttle_seconds = max_throttle_seconds
        self._random = random.Random(random_seed)
        self._batch_stack: list[BatchState] = []
        self._entrypoint_name: Optional[str] = None
        self._entrypoint_started_at: Optional[float] = None
        self.resource_guard = ResourceSafetyGuard()
        self.io_manager = io_manager or IOManager(
            before_write=self._before_queued_write,
            after_write=self._after_queued_write,
        )
        self.build_pipeline = BuildPipeline()
        self.validation_pipeline = ValidationPipeline()
        self.injection_pipeline = InjectionPipeline()

    @property
    def current_batch(self) -> Optional[BatchState]:
        if not self._batch_stack:
            return None
        return self._batch_stack[-1]

    def next_delay_seconds(self) -> float:
        return self._random.uniform(self.min_throttle_seconds, self.max_throttle_seconds)

    def run_entrypoint(self, entrypoint_name: str, callback: Callable[[], Any]) -> Any:
        self._entrypoint_name = entrypoint_name
        self._entrypoint_started_at = time.monotonic()
        try:
            result = callback()
            if self.io_manager.has_pending_writes:
                self.commit(reason=f"{entrypoint_name}:final-commit")
            return result
        finally:
            self.io_manager.clear()
            self._batch_stack.clear()
            self._entrypoint_name = None
            self._entrypoint_started_at = None

    def process_batch(
        self,
        items: Iterable[Any],
        item_processor: Callable[[Any], Any],
        *,
        batch_size: int = DEFAULT_BATCH_SIZE,
        pipeline: str = "validation",
        batch_validator: Optional[Callable[[list[Any]], Any]] = None,
        flush_writes: bool = False,
        file_operation: bool = False,
        stop_when: Optional[Callable[[Any, list[Any], list[Any]], bool]] = None,
        batch_name: Optional[str] = None,
    ) -> list[Any]:
        normalized_batch_size = max(1, min(batch_size, self.max_operations_per_batch))
        collected_results: list[Any] = []

        for batch_index, chunk in enumerate(self._chunked(items, normalized_batch_size), start=1):
            current_batch_name = batch_name or "batch"
            self._push_batch(current_batch_name, pipeline, batch_index)
            batch_results: list[Any] = []
            stop_requested = False
            try:
                for item in chunk:
                    result = self.run_operation(
                        lambda item=item: item_processor(item),
                        label=f"{pipeline}:{current_batch_name}",
                        file_operation=file_operation,
                    )
                    batch_results.append(result)
                    collected_results.append(result)
                    if stop_when and stop_when(result, batch_results, collected_results):
                        stop_requested = True
                        break

                if batch_validator is not None:
                    self.validation_pipeline.validate_batch(
                        self,
                        f"{pipeline}:{current_batch_name}:{batch_index}",
                        lambda batch_results=batch_results: batch_validator(batch_results),
                    )

                if flush_writes and self.io_manager.has_pending_writes:
                    self.commit(reason=f"{pipeline}:{current_batch_name}:{batch_index}")
            finally:
                self._pop_batch()

            if stop_requested:
                break

        return collected_results

    def validate_batch(
        self,
        batch_name: str,
        validator: Callable[[], Any],
    ) -> Any:
        return self.validation_pipeline.validate_batch(self, batch_name, validator)

    def commit(self, reason: str = "explicit-commit") -> list[Path]:
        implicit_batch = False
        if self.current_batch is None:
            self._push_batch(reason, "build", 1)
            implicit_batch = True
        try:
            return self.build_pipeline.commit_batch(self, reason=reason)
        finally:
            if implicit_batch:
                self._pop_batch()

    def queue_text_write(
        self,
        file_path: Path | str,
        content: str,
        *,
        required_markers: Optional[list[str]] = None,
        encoding: str = "utf-8",
    ) -> None:
        self.io_manager.queue_text_write(
            Path(file_path),
            content,
            required_markers=required_markers or [],
            encoding=encoding,
        )

    def queue_json_write(
        self,
        file_path: Path | str,
        payload: Any,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> None:
        self.io_manager.queue_json_write(
            Path(file_path),
            payload,
            indent=indent,
            ensure_ascii=ensure_ascii,
        )

    def ensure_directory(self, directory: Path | str) -> Path:
        path = Path(directory)
        self.run_operation(
            lambda: path.mkdir(parents=True, exist_ok=True),
            label=f"mkdir:{path.name}",
            file_operation=True,
        )
        return path

    def read_text(
        self,
        file_path: Path | str,
        *,
        encoding: str = "utf-8",
        default: Optional[str] = None,
    ) -> Optional[str]:
        path = Path(file_path)
        return self.run_operation(
            lambda: path.read_text(encoding=encoding) if path.exists() else default,
            label=f"read:{path.name}",
            file_operation=True,
        )

    def read_json(
        self,
        file_path: Path | str,
        *,
        default: Optional[Any] = None,
        encoding: str = "utf-8",
    ) -> Any:
        content = self.read_text(file_path, encoding=encoding, default=None)
        if content is None:
            return default
        return json.loads(content)

    def list_directory(self, directory: Path | str) -> list[Path]:
        path = Path(directory)
        return self.run_operation(
            lambda: sorted(path.iterdir(), key=lambda item: item.name) if path.exists() else [],
            label=f"list:{path.name}",
            file_operation=True,
        )

    def run_subprocess(
        self,
        command: list[str],
        *,
        cwd: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
        capture_output: bool = True,
        text: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return self.run_operation(
            lambda: subprocess.run(
                command,
                cwd=cwd,
                env=env,
                timeout=timeout,
                capture_output=capture_output,
                text=text,
                check=False,
            ),
            label=f"subprocess:{Path(command[0]).name}",
            file_operation=False,
        )

    def run_operation(
        self,
        operation: Callable[[], Any],
        *,
        label: str,
        file_operation: bool = False,
    ) -> Any:
        implicit_batch = False
        if self.current_batch is None:
            self._push_batch(label, "implicit", 1)
            implicit_batch = True

        try:
            self.resource_guard.pause_if_needed(self)
            self._register_operation(file_operation=file_operation, label=label)
            return operation()
        finally:
            time.sleep(self.next_delay_seconds())
            if implicit_batch:
                self._pop_batch()

    def raise_if_batch_expired(self) -> None:
        batch = self.current_batch
        if batch is None:
            return
        if batch.elapsed_seconds > self.max_runtime_per_batch_seconds:
            raise BatchRuntimeExceeded(
                f"Batch '{batch.name}' exceeded {self.max_runtime_per_batch_seconds}s."
            )

    def _before_queued_write(self, write: QueuedWrite) -> None:
        self.resource_guard.pause_if_needed(self)
        self._register_operation(
            file_operation=True,
            label=f"queued-write:{write.path.name}",
        )

    def _after_queued_write(self, write: QueuedWrite) -> None:
        time.sleep(self.next_delay_seconds())

    def _register_operation(self, *, file_operation: bool, label: str) -> None:
        batch = self.current_batch
        if batch is None:
            raise ExecutionControlError(
                f"No active batch while registering operation '{label}'."
            )

        self.raise_if_batch_expired()
        batch.operations += 1
        if batch.operations > self.max_operations_per_batch:
            raise OperationLimitExceeded(
                f"Batch '{batch.name}' exceeded {self.max_operations_per_batch} operations."
            )

        if file_operation:
            batch.file_operations += 1
            if batch.file_operations > self.max_file_operations_per_batch:
                raise FileOperationLimitExceeded(
                    f"Batch '{batch.name}' exceeded "
                    f"{self.max_file_operations_per_batch} file operations."
                )

    def _push_batch(self, name: str, pipeline: str, batch_index: int) -> None:
        self._batch_stack.append(
            BatchState(
                name=name,
                pipeline=pipeline,
                batch_index=batch_index,
                started_at=time.monotonic(),
            )
        )

    def _pop_batch(self) -> None:
        if self._batch_stack:
            self._batch_stack.pop()

    @staticmethod
    def _chunked(items: Iterable[Any], batch_size: int) -> Iterable[list[Any]]:
        chunk: list[Any] = []
        for item in items:
            chunk.append(item)
            if len(chunk) == batch_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


_CONTROLLER_CACHE: dict[Path, ExecutionController] = {}


def get_execution_controller(project_root: Path | str) -> ExecutionController:
    normalized_root = Path(project_root).resolve()
    controller = _CONTROLLER_CACHE.get(normalized_root)
    if controller is None:
        controller = ExecutionController(normalized_root)
        _CONTROLLER_CACHE[normalized_root] = controller
    return controller
