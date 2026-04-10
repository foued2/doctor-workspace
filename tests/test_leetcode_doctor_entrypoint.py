from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = PROJECT_ROOT / "leetcode-tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import leetcode_doctor  # noqa: E402


class LeetCodeDoctorEntrypointTests(unittest.TestCase):
    def test_find_problem_file_accepts_absolute_path(self) -> None:
        file_path = (PROJECT_ROOT / "solutions" / "001 to 100" / "1. Two Sum.py").resolve()

        self.assertEqual(leetcode_doctor.find_problem_file(str(file_path)), file_path)

    def test_run_test_cases_uses_embedded_test_mode(self) -> None:
        file_path = (PROJECT_ROOT / "solutions" / "001 to 100" / "1. Two Sum.py").resolve()
        fake_result = SimpleNamespace(stdout="", stderr="", returncode=0)

        with mock.patch.object(
            leetcode_doctor.CONTROLLER,
            "run_subprocess",
            return_value=fake_result,
        ) as run_subprocess:
            result = leetcode_doctor.run_test_cases(file_path)

        self.assertEqual(result["pass_rate"], 1.0)
        self.assertEqual(
            run_subprocess.call_args.kwargs["env"]["LEETCODE_DOCTOR_FILE_MODE"],
            "run-tests",
        )


if __name__ == "__main__":
    unittest.main()
