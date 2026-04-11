from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Optional


@dataclass(frozen=True)
class QueuedWrite:
    path: Path
    content: str
    required_markers: tuple[str, ...]
    encoding: str = "utf-8"


class IOManager:
    """Queues file writes in memory and flushes them only on commit."""

    def __init__(
        self,
        *,
        before_write: Optional[Callable[[QueuedWrite], None]] = None,
        after_write: Optional[Callable[[QueuedWrite], None]] = None,
    ) -> None:
        self._queue: list[QueuedWrite] = []
        self._before_write = before_write
        self._after_write = after_write

    @property
    def has_pending_writes(self) -> bool:
        return bool(self._queue)

    def peek(self) -> list[QueuedWrite]:
        return list(self._queue)

    def clear(self) -> None:
        self._queue.clear()

    def queue_text_write(
        self,
        path: Path | str,
        content: str,
        *,
        required_markers: Iterable[str] = (),
        encoding: str = "utf-8",
    ) -> None:
        self._queue.append(
            QueuedWrite(
                path=Path(path),
                content=content,
                required_markers=tuple(required_markers),
                encoding=encoding,
            )
        )

    def queue_json_write(
        self,
        path: Path | str,
        payload: Any,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
        encoding: str = "utf-8",
    ) -> None:
        self.queue_text_write(
            path,
            json.dumps(payload, indent=indent, ensure_ascii=ensure_ascii),
            encoding=encoding,
        )

    def flush(self) -> list[Path]:
        pending = self.peek()
        if not pending:
            return []

        written_paths: list[Path] = []
        try:
            for write in pending:
                if self._before_write:
                    self._before_write(write)
                self._write_atomic(write)
                written_paths.append(write.path)
                if self._after_write:
                    self._after_write(write)
        except Exception:
            self._queue = [write for write in pending if write.path not in written_paths]
            raise

        self.clear()
        return written_paths

    @staticmethod
    def _write_atomic(write: QueuedWrite) -> None:
        write.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = write.path.with_suffix(write.path.suffix + ".tmp")

        try:
            with open(tmp_path, "w", encoding=write.encoding) as handle:
                handle.write(write.content)
                handle.flush()
                try:
                    os.fsync(handle.fileno())
                except OSError:
                    pass
            os.replace(tmp_path, write.path)
        except Exception:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise
