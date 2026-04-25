import importlib.util
import pathlib
import unittest

from doctor.ingest.unified_engine import _check_structural_modifier


ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCTOR_SCRIPT = ROOT / "doctor.py"

spec = importlib.util.spec_from_file_location("doctor_cli", DOCTOR_SCRIPT)
doctor_cli = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(doctor_cli)


class Gate2ModifierDetectionTests(unittest.TestCase):
    def test_gate2_ignores_problem_statement_phrasing(self) -> None:
        parsed_model = {
            "objective": (
                "Arrange the integers so each adjacent difference is divisible "
                "by at least one value in k."
            ),
            "constraints": ["3 <= n <= 5000", "1 <= len(k) <= 10"],
            "edge_conditions": [],
        }

        result = doctor_cli.gate2_modifiers(parsed_model, "arrange_numbers_divisible")

        self.assertTrue(result["passed"])
        self.assertEqual(result["found_modifiers"], [])
        self.assertIsNone(result["modifier_class"])

    def test_gate2_detects_modifier_in_edge_conditions(self) -> None:
        parsed_model = {
            "constraints": [],
            "edge_conditions": ["Values are non-negative."],
        }

        result = doctor_cli.gate2_modifiers(parsed_model, "arrange_numbers_divisible")

        self.assertTrue(result["passed"])
        self.assertIn("non-negative", result["found_modifiers"])
        self.assertEqual(result["modifier_class"], "Class 2")

    def test_unified_engine_modifier_check_uses_parsed_fields(self) -> None:
        has_modifier, reason = _check_structural_modifier(
            ["1 <= n <= 5000"],
            ["except duplicates"],
            "arrange_numbers_divisible",
        )

        self.assertTrue(has_modifier)
        self.assertIn("except", reason)


if __name__ == "__main__":
    unittest.main()
