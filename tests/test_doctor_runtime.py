from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from doctor_runtime import (
    DOCTOR_TEST_MODE_ENV,
    DOCTOR_TEST_MODE_VALUE,
    is_doctor_managed_file,
    run_doctor_or_embedded_tests,
)


class DoctorRuntimeTests(unittest.TestCase):
    def test_is_doctor_managed_file_requires_workflow_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "managed.py"
            file_path.write_text(
                "TODO WORKFLOW\nTODO #2\nTODO #3\nTODO #4\n",
                encoding="utf-8",
            )

            self.assertTrue(is_doctor_managed_file(file_path))

    def test_run_doctor_or_embedded_tests_runs_tests_in_test_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "managed.py"
            file_path.write_text(
                "TODO WORKFLOW\nTODO #2\nTODO #3\nTODO #4\n",
                encoding="utf-8",
            )
            called: list[str] = []

            with mock.patch("doctor_runtime.subprocess.run") as subprocess_run:
                exit_code = run_doctor_or_embedded_tests(
                    file_path,
                    lambda: called.append("tests"),
                    env={DOCTOR_TEST_MODE_ENV: DOCTOR_TEST_MODE_VALUE},
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(called, ["tests"])
            subprocess_run.assert_not_called()

    def test_run_doctor_or_embedded_tests_invokes_doctor_for_managed_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            tools_dir = project_root / "leetcode-tools"
            problem_dir = project_root / "001 to 100"
            tools_dir.mkdir()
            problem_dir.mkdir()

            (project_root / "execution_controller.py").write_text("# marker\n", encoding="utf-8")
            (tools_dir / "leetcode_doctor.py").write_text("# marker\n", encoding="utf-8")
            file_path = problem_dir / "1. Example.py"
            file_path.write_text(
                "TODO WORKFLOW\nTODO #2\nTODO #3\nTODO #4\n",
                encoding="utf-8",
            )

            with mock.patch(
                "doctor_runtime.subprocess.run",
                return_value=SimpleNamespace(returncode=0),
            ) as subprocess_run:
                exit_code = run_doctor_or_embedded_tests(file_path, lambda: None)

            self.assertEqual(exit_code, 0)
            subprocess_run.assert_called_once()
            command = subprocess_run.call_args.args[0]
            self.assertEqual(command[2], str(file_path.resolve()))
            self.assertEqual(
                subprocess_run.call_args.kwargs["cwd"],
                str(project_root.resolve()),
            )


if __name__ == "__main__":
    unittest.main()
