import unittest
import os
from pathlib import Path

from execution_controller import (
    ExecutionController,
    FileOperationLimitExceeded,
    OperationLimitExceeded,
)
from io_manager import IOManager


class ExecutionHarnessTests(unittest.TestCase):
    def test_io_manager_flushes_only_on_commit(self) -> None:
        with self.subTest("queued writes stay in memory until flush"):
            tmp_path = Path(self.id().replace(".", "_"))
            if tmp_path.exists():
                for child in tmp_path.iterdir():
                    if child.is_file():
                        child.unlink()
                tmp_path.rmdir()
            tmp_path.mkdir()
            self.addCleanup(lambda: self._cleanup_dir(tmp_path))

            target = tmp_path / "queued.txt"
            manager = IOManager()

            manager.queue_text_write(target, "queued write", required_markers=["queued"])

            self.assertFalse(target.exists())

            written = manager.flush()

            self.assertEqual(written, [target])
            self.assertEqual(target.read_text(encoding="utf-8"), "queued write")

    def test_controller_flushes_writes_at_batch_end(self) -> None:
        tmp_path = Path(self.id().replace(".", "_"))
        tmp_path.mkdir(exist_ok=True)
        self.addCleanup(lambda: self._cleanup_dir(tmp_path))

        controller = ExecutionController(
            tmp_path,
            min_throttle_seconds=0.0,
            max_throttle_seconds=0.0,
            random_seed=0,
        )
        seen_paths: list[Path] = []

        def processor(item: int) -> Path:
            file_path = tmp_path / f"{item}.txt"
            controller.queue_text_write(
                file_path,
                str(item),
                required_markers=[str(item)],
            )
            self.assertFalse(file_path.exists())
            seen_paths.append(file_path)
            return file_path

        controller.run_entrypoint(
            "test-batch-flush",
            lambda: controller.process_batch(
                [1, 2, 3],
                processor,
                batch_size=2,
                pipeline="build",
                flush_writes=True,
            ),
        )

        self.assertEqual(
            [path.read_text(encoding="utf-8") for path in seen_paths],
            ["1", "2", "3"],
        )

    def test_controller_raises_when_batch_operations_exceed_limit(self) -> None:
        tmp_path = Path(self.id().replace(".", "_"))
        tmp_path.mkdir(exist_ok=True)
        self.addCleanup(lambda: self._cleanup_dir(tmp_path))

        controller = ExecutionController(
            tmp_path,
            max_operations_per_batch=1,
            min_throttle_seconds=0.0,
            max_throttle_seconds=0.0,
            random_seed=0,
        )

        def processor(_: int) -> None:
            controller.run_operation(lambda: None, label="extra-operation")

        with self.assertRaises(OperationLimitExceeded):
            controller.run_entrypoint(
                "test-operation-limit",
                lambda: controller.process_batch(
                    [1],
                    processor,
                    batch_size=1,
                    pipeline="validation",
                    flush_writes=False,
                ),
            )

    def test_controller_blocks_commit_when_file_budget_is_exceeded(self) -> None:
        tmp_path = Path(self.id().replace(".", "_"))
        tmp_path.mkdir(exist_ok=True)
        self.addCleanup(lambda: self._cleanup_dir(tmp_path))

        controller = ExecutionController(
            tmp_path,
            max_file_operations_per_batch=1,
            min_throttle_seconds=0.0,
            max_throttle_seconds=0.0,
            random_seed=0,
        )

        def queue_two_writes() -> None:
            controller.queue_text_write(tmp_path / "first.txt", "first", required_markers=["first"])
            controller.queue_text_write(tmp_path / "second.txt", "second", required_markers=["second"])
            controller.commit(reason="test-file-budget")

        with self.assertRaises(FileOperationLimitExceeded):
            controller.run_entrypoint("test-file-limit", queue_two_writes)

        self.assertFalse((tmp_path / "first.txt").exists())
        self.assertFalse((tmp_path / "second.txt").exists())

    def test_run_subprocess_forwards_environment(self) -> None:
        tmp_path = Path(self.id().replace(".", "_"))
        tmp_path.mkdir(exist_ok=True)
        self.addCleanup(lambda: self._cleanup_dir(tmp_path))

        controller = ExecutionController(
            tmp_path,
            min_throttle_seconds=0.0,
            max_throttle_seconds=0.0,
            random_seed=0,
        )

        result = controller.run_subprocess(
            [
                os.sys.executable,
                "-c",
                "import os; print(os.environ.get('EXECUTION_CONTROLLER_TEST_ENV', 'missing'))",
            ],
            env={"EXECUTION_CONTROLLER_TEST_ENV": "present"},
        )

        self.assertEqual(result.stdout.strip(), "present")

    @staticmethod
    def _cleanup_dir(path: Path) -> None:
        if not path.exists():
            return
        for child in path.iterdir():
            if child.is_file():
                child.unlink()
        path.rmdir()


if __name__ == "__main__":
    unittest.main()
