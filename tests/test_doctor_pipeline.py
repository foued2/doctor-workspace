import importlib.util
import pathlib
import unittest

from doctor.core.test_executor import TestExecutor, _results_equal


ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCTOR_SCRIPT = ROOT / "doctor.py"
SOLUTION_FILE = ROOT / "cf2225g.py"

spec = importlib.util.spec_from_file_location("doctor_cli", DOCTOR_SCRIPT)
doctor_cli = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(doctor_cli)


class DoctorPipelineTests(unittest.TestCase):
    def test_gate3_reads_solution_file(self) -> None:
        result = doctor_cli.gate3_solution(str(SOLUTION_FILE))

        self.assertTrue(result["passed"])
        self.assertIn("def solve_case", result["solution_code"])
        self.assertEqual(result["solution_path"], str(SOLUTION_FILE))

    def test_results_equal_requires_strict_minus_one(self) -> None:
        self.assertFalse(_results_equal(None, -1))
        self.assertTrue(_results_equal(-1, -1))

    def test_executor_reports_honest_arrangement_result(self) -> None:
        code = SOLUTION_FILE.read_text(encoding="utf-8")
        report = TestExecutor().verify("arrange_numbers_divisible", code)
        statuses = {result.label: result.passed for result in report.results}

        self.assertEqual(report.passed, 3)
        self.assertEqual(report.total, 4)
        self.assertTrue(statuses["sample"])
        self.assertTrue(statuses["impossible"])
        self.assertTrue(statuses["trivial_k1"])
        self.assertFalse(statuses["cross_boundary"])


if __name__ == "__main__":
    unittest.main()
