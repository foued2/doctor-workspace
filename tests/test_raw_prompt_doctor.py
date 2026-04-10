from __future__ import annotations

import unittest

from doctor import RawPromptDoctor


class RawPromptDoctorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doctor = RawPromptDoctor()

    def test_conflicting_examples_resolution_returns_partial_without_crashing(self):
        prompt = """
        The sample label from memo conflicts with the prose and the proposed answer
        follows the explicit prose constraints instead.
        """

        prediction = self.doctor.predict(prompt)

        self.assertEqual(prediction["label"], "partial")
        self.assertIs(prediction["conflict_detected"], True)
        self.assertIs(prediction["priority_rule_applied"], True)
        self.assertIs(prediction["discarded_weaker_constraints"], True)
        self.assertEqual(prediction["decision_path"], ["R2:conflicting_examples_resolved"])

    def test_explain_includes_claims_for_conflicting_examples_case(self):
        prompt = """
        The sample label from memo conflicts with the prose and the proposed answer
        follows the explicit prose constraints instead.
        """

        explanation = self.doctor.explain(prompt)

        self.assertEqual(explanation["label"], "partial")
        self.assertGreaterEqual(explanation["claims"]["scores"]["conflicting_examples_score"], 0.85)
        self.assertEqual(
            explanation["claims"]["bias_context"]["completeness_vs_conflict_independence"],
            "enforced_layer2",
        )

    def test_ground_truth_leak_still_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "Ground-truth leak detected"):
            self.doctor.predict("This prompt contains a ground_truth label.")


if __name__ == "__main__":
    unittest.main()
