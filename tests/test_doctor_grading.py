"""
Test Suite for Longitudinal Doctor Grading System
===================================================

Tests the persistent, multi-factor, longitudinal skill tracking system.

Test Suites:
    A — Consistency Test
    B — Improvement Simulation
    C — Noise Resistance Test
    D — Category Separation Test
    E — Persistence Test
    F — Long-Horizon Drift Test
"""

import json
import os
import sys
import copy
import random
from pathlib import Path
from unittest import TestCase, main, TestLoader, TestSuite, TextTestRunner

# Ensure project root is in path
TOOLS_ROOT = Path(__file__).resolve().parent / "leetcode-tools"
PROJECT_ROOT = TOOLS_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

# Import grading functions directly from leetcode_doctor
from leetcode_doctor import (
    _default_skill_state,
    load_skill_state,
    save_skill_state,
    extract_features,
    update_skill_state,
    compute_trend_label,
    get_weak_areas,
    build_grading_output,
    DOCTOR_SKILL_STATE_FILE,
    SKILL_CATEGORIES,
    OVERALL_ACCURACY_WINDOW,
    TREND_WINDOW,
    CONSISTENCY_WINDOW,
    TREND_IMPROVING_THRESHOLD,
    TREND_DEGRADING_THRESHOLD,
)


# ============================================================
# Helper: simulate a problem evaluation without AI/IO
# ============================================================
def simulate_evaluation(
    state: dict,
    *,
    correctness: float,
    runtime_score: float,
    memory_score: float,
    topic: str,
    error_type: str,
) -> dict:
    """Run a single problem simulation and return grading output."""
    features = {
        "correctness": correctness,
        "runtime_score": runtime_score,
        "memory_score": memory_score,
        "topic": topic,
        "error_type": error_type,
    }
    updated_state = update_skill_state(state, features)
    grading_output = build_grading_output(updated_state, features, {})
    return grading_output, updated_state


def simulate_simple_update(state: dict, *, correctness: float, topic: str) -> dict:
    """Simplified update for testing without full feature extraction."""
    features = {
        "correctness": correctness,
        "runtime_score": 0.8,
        "memory_score": 0.7,
        "topic": topic,
        "error_type": "none" if correctness == 1.0 else "edge_case",
    }
    return update_skill_state(state, features)


# ============================================================
# TEST SUITE A — Consistency Test
# ============================================================
class TestConsistency(TestCase):
    """Run 10 identical correct solutions. Verify score stabilizes upward then plateaus.
    No oscillation > 10%."""

    def test_10_identical_correct_solutions(self):
        state = _default_skill_state()
        scores = []

        for _ in range(10):
            state = simulate_simple_update(state, correctness=1.0, topic="string")
            scores.append(state["skills"]["string"]["score"])

        # Scores should be monotonically increasing (or stable at 1.0)
        for i in range(1, len(scores)):
            self.assertGreaterEqual(
                scores[i],
                scores[i - 1],
                f"Score dropped from {scores[i-1]} to {scores[i]} on iteration {i+1}",
            )

        # Final score should be 1.0 (all correct)
        self.assertAlmostEqual(scores[-1], 1.0, places=4)

    def test_no_oscillation_above_10_percent(self):
        state = _default_skill_state()
        scores = []

        for _ in range(10):
            state = simulate_simple_update(state, correctness=1.0, topic="dp")
            scores.append(state["skills"]["dp"]["score"])

        # Check for oscillation > 10%
        for i in range(1, len(scores)):
            diff = abs(scores[i] - scores[i - 1])
            self.assertLessEqual(
                diff,
                0.10,
                f"Oscillation detected: {diff:.4f} between step {i} and {i+1}",
            )

    def test_plateau_detection(self):
        state = _default_skill_state()
        scores = []

        for _ in range(10):
            state = simulate_simple_update(state, correctness=1.0, topic="greedy")
            scores.append(state["skills"]["greedy"]["score"])

        # After 10 perfect runs, the score should be very close to 1.0
        self.assertGreater(scores[-1], 0.9)

        # Run 5 more and verify plateau (no significant change)
        for _ in range(5):
            state = simulate_simple_update(state, correctness=1.0, topic="greedy")
            scores.append(state["skills"]["greedy"]["score"])

        # Last 5 scores should be within 0.05 of each other
        last_five = scores[-5:]
        self.assertLessEqual(
            max(last_five) - min(last_five),
            0.05,
            "Score not plateauing: still changing significantly",
        )


# ============================================================
# TEST SUITE B — Improvement Simulation
# ============================================================
class TestImprovementSimulation(TestCase):
    """Simulate sequence: wrong → wrong → partial → correct → correct
    Verify trend = improving and skill score increases monotonically."""

    def test_improvement_sequence(self):
        state = _default_skill_state()
        scores = []
        correctness_values = [0.0, 0.0, 0.5, 1.0, 1.0]

        for correctness in correctness_values:
            state = simulate_simple_update(state, correctness=correctness, topic="recursion")
            scores.append(state["skills"]["recursion"]["score"])

        # Trend should be improving
        trend = compute_trend_label(state)
        self.assertEqual(trend, "improving", f"Expected 'improving', got '{trend}'")

    def test_monotonic_increase_after_partial(self):
        """After partial→correct→correct, scores should not drop."""
        state = _default_skill_state()
        scores = []

        # Wrong twice
        state = simulate_simple_update(state, correctness=0.0, topic="dp")
        scores.append(state["skills"]["dp"]["score"])
        state = simulate_simple_update(state, correctness=0.0, topic="dp")
        scores.append(state["skills"]["dp"]["score"])

        # Partial
        state = simulate_simple_update(state, correctness=0.5, topic="dp")
        scores.append(state["skills"]["dp"]["score"])

        # Correct twice
        state = simulate_simple_update(state, correctness=1.0, topic="dp")
        scores.append(state["skills"]["dp"]["score"])
        state = simulate_simple_update(state, correctness=1.0, topic="dp")
        scores.append(state["skills"]["dp"]["score"])

        # From index 2 onwards (partial), scores should be monotonically increasing
        for i in range(3, len(scores)):
            self.assertGreaterEqual(
                scores[i],
                scores[i - 1],
                f"Score dropped from {scores[i-1]} to {scores[i]} during improvement phase",
            )

    def test_overall_accuracy_increases(self):
        state = _default_skill_state()
        accuracies = []

        correctness_values = [0.0, 0.0, 0.5, 1.0, 1.0]
        for correctness in correctness_values:
            state = simulate_simple_update(state, correctness=correctness, topic="graph")
            accuracies.append(state["overall_accuracy"])

        # Overall accuracy should increase over time
        self.assertGreater(accuracies[-1], accuracies[0])


# ============================================================
# TEST SUITE C — Noise Resistance Test
# ============================================================
class TestNoiseResistance(TestCase):
    """Random mix of correct/incorrect. Verify no extreme score swings
    and smoothing works."""

    def test_no_extreme_swings(self):
        random.seed(42)
        state = _default_skill_state()
        scores = []

        for _ in range(50):
            correctness = random.choice([0.0, 0.5, 1.0])
            state = simulate_simple_update(state, correctness=correctness, topic="string")
            scores.append(state["skills"]["string"]["score"])

        # Check that no single step changes by more than 0.5
        # (Early iterations can have larger swings when count is low)
        for i in range(1, len(scores)):
            diff = abs(scores[i] - scores[i - 1])
            self.assertLessEqual(
                diff,
                0.50,
                f"Extreme score swing: {diff:.4f} at step {i+1}",
            )

        # After first 10 iterations, swings should be smaller (< 0.2)
        for i in range(10, len(scores)):
            diff = abs(scores[i] - scores[i - 1])
            self.assertLessEqual(
                diff,
                0.20,
                f"Late-stage swing too large: {diff:.4f} at step {i+1}",
            )

    def test_smoothing_effect(self):
        """After many mixed results, score should stabilize around mean correctness."""
        random.seed(123)
        state = _default_skill_state()

        # 70% correct, 30% wrong
        correctness_sequence = [1.0 if random.random() < 0.7 else 0.0 for _ in range(100)]

        for correctness in correctness_sequence:
            state = simulate_simple_update(state, correctness=correctness, topic="dp")

        # Final score should be close to 0.7 (the mean correctness rate)
        final_score = state["skills"]["dp"]["score"]
        self.assertAlmostEqual(final_score, 0.7, delta=0.15)

    def test_robustness_stability(self):
        """Robustness score should not fluctuate wildly."""
        random.seed(99)
        state = _default_skill_state()
        robustness_scores = []

        for _ in range(30):
            correctness = random.choice([0.0, 1.0])
            error_type = "none" if correctness == 1.0 else "runtime"
            features = {
                "correctness": correctness,
                "runtime_score": 0.8,
                "memory_score": 0.7,
                "topic": "graph",
                "error_type": error_type,
            }
            state = update_skill_state(state, features)
            robustness_scores.append(state["robustness"])

        # Robustness should change gradually, not jump
        # Early iterations can have larger changes (up to 0.5)
        for i in range(1, len(robustness_scores)):
            diff = abs(robustness_scores[i] - robustness_scores[i - 1])
            # Allow larger swings in early iterations
            max_allowed = 0.5 if i < 5 else 0.2
            self.assertLessEqual(
                diff,
                max_allowed,
                f"Robustness jumped by {diff:.4f} at step {i+1}",
            )


# ============================================================
# TEST SUITE D — Category Separation Test
# ============================================================
class TestCategorySeparation(TestCase):
    """Feed DP + Graph + String problems alternately.
    Verify dp skill changes independently of graph skill. No cross-contamination."""

    def test_independent_skill_updates(self):
        state = _default_skill_state()

        # Run 5 DP problems
        for _ in range(5):
            state = simulate_simple_update(state, correctness=1.0, topic="dp")

        dp_score_after_5 = state["skills"]["dp"]["score"]
        graph_score_after_5 = state["skills"]["graph"]["score"]

        # Graph score should still be 0.0 (never updated)
        self.assertEqual(graph_score_after_5, 0.0)
        self.assertGreater(dp_score_after_5, 0.0)

    def test_no_cross_contamination(self):
        state = _default_skill_state()

        # Alternate: DP, Graph, String, DP, Graph, String
        topics = ["dp", "graph", "string"] * 5
        for topic in topics:
            state = simulate_simple_update(state, correctness=1.0, topic=topic)

        # All three skills should have score = 1.0 (all correct)
        for topic in topics:
            self.assertAlmostEqual(
                state["skills"][topic]["score"],
                1.0,
                places=4,
                msg=f"{topic} score should be 1.0",
            )

        # But each skill's count should be exactly 5 (only updated when that topic appeared)
        for topic in ["dp", "graph", "string"]:
            self.assertEqual(
                state["skills"][topic]["count"],
                5,
                msg=f"{topic} count should be exactly 5",
            )

    def test_skill_specific_accuracy(self):
        """DP accuracy should not affect Graph accuracy."""
        state = _default_skill_state()

        # 10 correct DP problems
        for _ in range(10):
            state = simulate_simple_update(state, correctness=1.0, topic="dp")

        # 5 wrong Graph problems
        for _ in range(5):
            state = simulate_simple_update(state, correctness=0.0, topic="graph")

        # DP score should still be 1.0
        self.assertAlmostEqual(state["skills"]["dp"]["score"], 1.0, places=4)

        # Graph score should be 0.0
        self.assertAlmostEqual(state["skills"]["graph"]["score"], 0.0, places=4)

    def test_weak_areas_independence(self):
        """Weak areas should reflect per-skill performance, not global."""
        state = _default_skill_state()

        # Good at DP, bad at Graph
        for _ in range(5):
            state = simulate_simple_update(state, correctness=1.0, topic="dp")
        for _ in range(5):
            state = simulate_simple_update(state, correctness=0.0, topic="graph")

        weak = get_weak_areas(state)
        self.assertIn("graph", weak, "Graph should be a weak area")
        self.assertNotIn("dp", weak, "DP should NOT be a weak area")


# ============================================================
# TEST SUITE E — Persistence Test
# ============================================================
class TestPersistence(TestCase):
    """Run 5 updates, reload JSON, verify state is identical. No corruption."""

    def setUp(self):
        """Backup existing skill state file if present."""
        self.backup_path = DOCTOR_SKILL_STATE_FILE.with_suffix(".json.backup")
        if DOCTOR_SKILL_STATE_FILE.exists():
            DOCTOR_SKILL_STATE_FILE.rename(self.backup_path)

    def tearDown(self):
        """Restore original skill state file."""
        if self.backup_path.exists():
            if DOCTOR_SKILL_STATE_FILE.exists():
                DOCTOR_SKILL_STATE_FILE.unlink()
            self.backup_path.rename(DOCTOR_SKILL_STATE_FILE)
        elif DOCTOR_SKILL_STATE_FILE.exists():
            # Clean up test file
            DOCTOR_SKILL_STATE_FILE.unlink()

    def test_persistence_and_reload(self):
        """Run 5 updates, save, reload, verify identical."""
        state = _default_skill_state()

        # Run 5 updates on different topics
        topics = ["dp", "graph", "string", "dp", "greedy"]
        for topic in topics:
            state = simulate_simple_update(state, correctness=1.0, topic=topic)

        # Save state
        save_skill_state(state)

        # Verify file exists
        self.assertTrue(
            DOCTOR_SKILL_STATE_FILE.exists(),
            "Skill state file should exist after save",
        )

        # Reload state
        reloaded_state = load_skill_state()

        # Verify critical fields are identical
        self.assertEqual(
            state["total_problems"],
            reloaded_state["total_problems"],
            "total_problems mismatch after reload",
        )
        self.assertAlmostEqual(
            state["overall_accuracy"],
            reloaded_state["overall_accuracy"],
            places=4,
            msg="overall_accuracy mismatch after reload",
        )

        for cat in SKILL_CATEGORIES:
            self.assertAlmostEqual(
                state["skills"][cat]["score"],
                reloaded_state["skills"][cat]["score"],
                places=4,
                msg=f"{cat} score mismatch after reload",
            )
            self.assertEqual(
                state["skills"][cat]["count"],
                reloaded_state["skills"][cat]["count"],
                msg=f"{cat} count mismatch after reload",
            )

        self.assertEqual(
            state["recent_trend"],
            reloaded_state["recent_trend"],
            "recent_trend mismatch after reload",
        )

    def test_no_corruption_on_repeated_saves(self):
        """Save state 10 times, verify JSON remains valid."""
        state = _default_skill_state()

        for i in range(10):
            state = simulate_simple_update(state, correctness=0.5, topic="recursion")
            save_skill_state(state)

            # Verify file is valid JSON
            try:
                with open(DOCTOR_SKILL_STATE_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.assertIsInstance(loaded, dict)
            except json.JSONDecodeError as e:
                self.fail(f"JSON corrupted after save #{i+1}: {e}")

    def test_state_survives_intermediate_crash_simulation(self):
        """Simulate crash by checking file is readable mid-process."""
        state = _default_skill_state()

        # Run 3 updates, save
        for _ in range(3):
            state = simulate_simple_update(state, correctness=1.0, topic="dp")
        save_skill_state(state)

        # Verify file readable
        with open(DOCTOR_SKILL_STATE_FILE, "r", encoding="utf-8") as f:
            mid_state = json.load(f)

        self.assertEqual(mid_state["total_problems"], 3)

        # Run 2 more updates
        for _ in range(2):
            state = simulate_simple_update(state, correctness=0.0, topic="graph")
        save_skill_state(state)

        # Verify final state
        final_state = load_skill_state()
        self.assertEqual(final_state["total_problems"], 5)


# ============================================================
# Additional Validation Tests
# ============================================================
class TestUpdateRulesStrictness(TestCase):
    """Verify update rules match specification exactly."""

    def test_skill_update_formula(self):
        """new_score = (old_score * count + current_score) / (count + 1)"""
        state = _default_skill_state()

        # First update: (0.0 * 0 + 1.0) / (0 + 1) = 1.0
        state = simulate_simple_update(state, correctness=1.0, topic="dp")
        self.assertAlmostEqual(state["skills"]["dp"]["score"], 1.0, places=4)
        self.assertEqual(state["skills"]["dp"]["count"], 1)

        # Second update: (1.0 * 1 + 0.5) / (1 + 1) = 0.75
        state = simulate_simple_update(state, correctness=0.5, topic="dp")
        self.assertAlmostEqual(state["skills"]["dp"]["score"], 0.75, places=4)
        self.assertEqual(state["skills"]["dp"]["count"], 2)

        # Third update: (0.75 * 2 + 1.0) / (2 + 1) = 0.8333...
        state = simulate_simple_update(state, correctness=1.0, topic="dp")
        self.assertAlmostEqual(state["skills"]["dp"]["score"], 0.8333, places=3)
        self.assertEqual(state["skills"]["dp"]["count"], 3)

    def test_efficiency_formula(self):
        """efficiency = 0.7 * runtime_score + 0.3 * memory_score"""
        state = _default_skill_state()
        features = {
            "correctness": 1.0,
            "runtime_score": 0.9,
            "memory_score": 0.6,
            "topic": "string",
            "error_type": "none",
        }
        state = update_skill_state(state, features)

        expected_efficiency = 0.7 * 0.9 + 0.3 * 0.6
        self.assertAlmostEqual(state["efficiency"], expected_efficiency, places=4)

    def test_overall_accuracy_window(self):
        """overall_accuracy = moving_average(last 50 results)"""
        state = _default_skill_state()

        # Run 60 updates (more than window size)
        for i in range(60):
            correctness = 1.0 if i >= 10 else 0.0  # First 10 wrong, next 50 correct
            state = simulate_simple_update(state, correctness=correctness, topic="string")

        # Should average last 50 only (all correct)
        self.assertAlmostEqual(state["overall_accuracy"], 1.0, places=4)

    def test_consistency_variance_based(self):
        """consistency based on variance of last N results (N=10-20)"""
        state = _default_skill_state()

        # Perfect consistency (all 1.0)
        for _ in range(15):
            state = simulate_simple_update(state, correctness=1.0, topic="dp")
        self.assertAlmostEqual(state["consistency"], 1.0, places=4)

        # Perfect inconsistency (alternating 0, 1)
        state = _default_skill_state()
        for i in range(20):
            correctness = 1.0 if i % 2 == 0 else 0.0
            state = simulate_simple_update(state, correctness=correctness, topic="dp")
        # High variance => lower consistency
        self.assertLess(state["consistency"], 0.8)


class TestTrendTracking(TestCase):
    """Verify trend computation rules."""

    def test_improving_trend(self):
        state = _default_skill_state()
        for _ in range(10):
            state = simulate_simple_update(state, correctness=0.0, topic="dp")
        for _ in range(10):
            state = simulate_simple_update(state, correctness=1.0, topic="dp")

        trend = compute_trend_label(state)
        self.assertEqual(trend, "improving")

    def test_degrading_trend(self):
        state = _default_skill_state()
        for _ in range(10):
            state = simulate_simple_update(state, correctness=1.0, topic="graph")
        for _ in range(10):
            state = simulate_simple_update(state, correctness=0.0, topic="graph")

        trend = compute_trend_label(state)
        self.assertEqual(trend, "degrading")

    def test_stable_trend(self):
        state = _default_skill_state()
        for _ in range(20):
            state = simulate_simple_update(state, correctness=0.5, topic="string")

        trend = compute_trend_label(state)
        self.assertEqual(trend, "stable")


# ============================================================
# TEST SUITE F — Long-Horizon Drift Test
# ============================================================
class TestLongHorizonDrift(TestCase):
    """Simulate 200 problems:
    - First 100: low performance (30-40%)
    - Next 100: high performance (80-90%)

    Check:
    - How long it takes for skill score to reflect improvement
    - Whether it ever reaches expected range

    If score lags heavily → model is too inert
    If score never catches up → model is flawed
    """

    def test_adaptation_speed(self):
        """Measure how many problems after the transition point until score starts rising."""
        random.seed(2026)
        state = _default_skill_state()
        scores = []

        # Phase 1: Low performance (30-40% correctness)
        for i in range(100):
            correctness = 1.0 if random.random() < 0.35 else 0.0
            state = simulate_simple_update(state, correctness=correctness, topic="dp")
            scores.append(state["skills"]["dp"]["score"])

        phase1_final_score = scores[-1]

        # Phase 2: High performance (80-90% correctness)
        for i in range(100):
            correctness = 1.0 if random.random() < 0.85 else 0.0
            state = simulate_simple_update(state, correctness=correctness, topic="dp")
            scores.append(state["skills"]["dp"]["score"])

        # Find the transition point (index 100)
        # Measure how many problems until score exceeds phase1 average by 0.05
        phase1_avg = sum(scores[:100]) / 100
        threshold = phase1_avg + 0.05

        adaptation_step = None
        for i in range(100, 200):
            if scores[i] > threshold:
                adaptation_step = i - 100  # Steps after transition
                break

        self.assertIsNotNone(
            adaptation_step,
            f"Score never exceeded phase 1 average + 0.05 ({threshold:.4f}). "
            f"Final score: {scores[-1]:.4f}. Model is too inert or flawed.",
        )

        # Adaptation should happen within 40 problems (reasonable for cumulative average with 100 history)
        # Cumulative average: after N new problems, weight of new data = N/(100+N)
        # At N=40, new data weight = 40/140 ≈ 29%, enough to shift average
        self.assertLessEqual(
            adaptation_step,
            40,
            f"Adaptation took {adaptation_step} problems. Expected ≤ 40. "
            f"Model may be too inert.",
        )

        print(f"\n  → Adaptation detected after {adaptation_step} problems")
        print(f"  → Phase 1 avg score: {phase1_avg:.4f}")
        print(f"  → Phase 2 final score: {scores[-1]:.4f}")

    def test_final_score_reaches_expected_range(self):
        """After 100 high-performance problems, score should reflect improvement.
        
        With cumulative averaging from 200 total problems:
        - Phase 1 (100 problems): ~35% correct
        - Phase 2 (100 problems): ~85% correct
        - Expected cumulative average: (35 + 85) / 2 = 60%
        """
        random.seed(2026)
        state = _default_skill_state()

        # Phase 1: Low performance (30-40%)
        for i in range(100):
            correctness = 1.0 if random.random() < 0.35 else 0.0
            state = simulate_simple_update(state, correctness=correctness, topic="graph")

        # Phase 2: High performance (80-90%)
        for i in range(100):
            correctness = 1.0 if random.random() < 0.85 else 0.0
            state = simulate_simple_update(state, correctness=correctness, topic="graph")

        final_score = state["skills"]["graph"]["score"]

        # With 200 problems total, cumulative average should be ~60%
        # Allow range: 0.50-0.70 (accounts for variance in randomness)
        self.assertGreater(
            final_score,
            0.50,
            f"Final score {final_score:.4f} is too low. "
            f"Model fails to reflect sustained improvement.",
        )

        self.assertLess(
            final_score,
            0.70,
            f"Final score {final_score:.4f} is too high for cumulative average. "
            f"Expected ~0.60 given 50/50 split of low/high performance.",
        )

        print(f"\n  → Final cumulative score: {final_score:.4f}")
        print(f"  → Expected range: 0.50-0.70 (cumulative average)")
        print(f"  → Note: Overall accuracy (50-window) shows recent performance")

    def test_trend_reflects_improvement(self):
        """Trend label should switch to 'improving' after transition point."""
        random.seed(2026)
        state = _default_skill_state()

        # Phase 1: Low performance
        for i in range(100):
            correctness = 1.0 if random.random() < 0.35 else 0.0
            state = simulate_simple_update(state, correctness=correctness, topic="string")

        # Phase 2: High performance
        for i in range(100):
            correctness = 1.0 if random.random() < 0.85 else 0.0
            state = simulate_simple_update(state, correctness=correctness, topic="string")

        trend = compute_trend_label(state)
        self.assertEqual(
            trend,
            "improving",
            f"Trend is '{trend}' but should be 'improving' after sustained high performance.",
        )

        print(f"\n  → Trend correctly detected as '{trend}'")

    def test_overall_accuracy_reflects_recent_performance(self):
        """Overall accuracy uses 50-result window, so should reflect recent high performance."""
        random.seed(2026)
        state = _default_skill_state()

        # Phase 1: Low performance
        for i in range(100):
            correctness = 1.0 if random.random() < 0.35 else 0.0
            state = simulate_simple_update(state, correctness=correctness, topic="dp")

        # Phase 2: High performance
        for i in range(100):
            correctness = 1.0 if random.random() < 0.85 else 0.0
            state = simulate_simple_update(state, correctness=correctness, topic="dp")

        # Overall accuracy should be close to recent performance (~85%)
        # since it only considers last 50 results
        overall_accuracy = state["overall_accuracy"]

        self.assertGreater(
            overall_accuracy,
            0.75,
            f"Overall accuracy {overall_accuracy:.4f} is too low. "
            f"50-result window should reflect recent high performance.",
        )

        self.assertLess(
            overall_accuracy,
            0.95,
            f"Overall accuracy {overall_accuracy:.4f} is too high. "
            f"Some noise expected even with 85% correctness rate.",
        )

        print(f"\n  → Overall accuracy (50-window): {overall_accuracy:.4f}")
        print(f"  → Expected range: 0.75-0.95")

    def test_inertia_is_mathematically_sound(self):
        """Verify that cumulative averaging behaves correctly:
        - Score changes are large when count is low
        - Score changes are small when count is high
        This is expected behavior, not a flaw."""
        state = _default_skill_state()
        deltas = []

        for i in range(200):
            old_score = state["skills"]["recursion"]["score"]
            state = simulate_simple_update(state, correctness=1.0, topic="recursion")
            new_score = state["skills"]["recursion"]["score"]
            deltas.append(new_score - old_score)

        # Early deltas should be large (first 10 problems)
        early_avg_delta = sum(deltas[:10]) / 10
        # Late deltas should be small (last 10 problems)
        late_avg_delta = sum(deltas[190:]) / 10

        self.assertGreater(
            early_avg_delta,
            late_avg_delta * 5,
            f"Early delta ({early_avg_delta:.4f}) should be much larger than "
            f"late delta ({late_avg_delta:.4f}). Cumulative averaging may be broken.",
        )

        # Late delta should be very small (approaching 0 as count increases)
        self.assertLess(
            late_avg_delta,
            0.01,
            f"Late delta ({late_avg_delta:.6f}) is too large. "
            f"Model should show diminishing updates at high counts.",
        )

        ratio = early_avg_delta / late_avg_delta if late_avg_delta > 0 else float('inf')
        print(f"\n  → Early avg delta (first 10): {early_avg_delta:.4f}")
        print(f"  → Late avg delta (last 10): {late_avg_delta:.6f}")
        print(f"  → Ratio: {ratio:.1f}x (or ∞ if late delta is ~0)")


class TestGradingOutputFormat(TestCase):
    """Verify output format matches specification."""

    def test_required_keys(self):
        state = _default_skill_state()
        state = simulate_simple_update(state, correctness=1.0, topic="dp")
        features = {
            "correctness": 1.0,
            "runtime_score": 0.9,
            "memory_score": 0.8,
            "topic": "dp",
            "error_type": "none",
        }
        output = build_grading_output(state, features, {})

        required_keys = {
            "correctness",
            "efficiency_score",
            "skill_update",
            "overall_progress",
            "weak_areas",
            "trend",
        }
        self.assertEqual(set(output.keys()), required_keys)

    def test_skill_update_structure(self):
        state = _default_skill_state()
        state = simulate_simple_update(state, correctness=1.0, topic="greedy")
        features = {
            "correctness": 1.0,
            "runtime_score": 0.9,
            "memory_score": 0.8,
            "topic": "greedy",
            "error_type": "none",
        }
        output = build_grading_output(state, features, {})

        self.assertIn("topic", output["skill_update"])
        self.assertIn("new_score", output["skill_update"])
        self.assertIn("count", output["skill_update"])
        self.assertEqual(output["skill_update"]["topic"], "greedy")


# ============================================================
# Test Runner with Report
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("LONGITUDINAL DOCTOR GRADING SYSTEM — TEST REPORT")
    print("=" * 70)
    print()

    # Run tests with verbosity
    test_loader = TestLoader()
    test_suite = TestSuite()

    # Add all test classes
    test_classes = [
        TestConsistency,
        TestImprovementSimulation,
        TestNoiseResistance,
        TestCategorySeparation,
        TestPersistence,
        TestUpdateRulesStrictness,
        TestTrendTracking,
        TestLongHorizonDrift,
        TestGradingOutputFormat,
    ]

    for test_class in test_classes:
        tests = test_loader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    test_runner = TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Print Summary
    print()
    print("=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Tests run:    {result.testsRun}")
    print(f"Failures:     {len(result.failures)}")
    print(f"Errors:       {len(result.errors)}")
    print(f"Skipped:      {len(result.skipped)}")
    print()

    if result.failures:
        print("FAILURE CASES:")
        for test, traceback in result.failures:
            print(f"  ✗ {test.id()}")
            print(f"    {traceback}")
        print()

    if result.errors:
        print("ERROR CASES:")
        for test, traceback in result.errors:
            print(f"  ✗ {test.id()}")
            print(f"    {traceback}")
        print()

    # Stability Verdict
    print("=" * 70)
    print("STABILITY VERDICT")
    print("=" * 70)

    if len(result.failures) == 0 and len(result.errors) == 0:
        print("✓ STABLE")
        print("  All tests passed. The grading system is fully stable.")
    elif len(result.failures) <= 2 and len(result.errors) == 0:
        print("⚠ PARTIALLY STABLE")
        print(f"  {len(result.failures)} minor failure(s). Review and fix recommended.")
    else:
        print("✗ UNSTABLE")
        print(f"  {len(result.failures)} failure(s), {len(result.errors)} error(s).")
        print("  System requires fixes before deployment.")

    print("=" * 70)
