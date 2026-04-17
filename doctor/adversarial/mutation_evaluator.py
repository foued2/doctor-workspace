"""
Doctor Mutation Evaluator — Measures test suite strength under adversarial degradation.

Measures:
  1. Reference solution passes E=1.0 (baseline)
  2. Mutated variants should fail at least some tests (mutation robustness)
  3. Adversarial tests should catch known failure patterns

Output: SuiteStrengthReport
  - reference_pass: bool
  - mutation_kill_rate: float (fraction of mutated variants caught by tests)
  - adversarial_coverage: int (number of adversarial cases runnable)
  - strength_score: float (composite)

Design constraints (enforced):
  - NO feedback from evaluation results to generation
  - All mutations generated before any evaluation runs
  - Adversarial tests are structural, not oracle-history-based
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .mutation_engine import MutationEngine, MutationResult
from .adversarial_generator import AdversarialGenerator, AdversarialTestCase


@dataclass
class SuiteStrengthReport:
    problem_id: str
    reference_pass: bool
    mutation_count: int
    mutations_killed: int
    mutation_kill_rate: float
    adversarial_count: int
    strength_score: float
    details: Dict[str, Any]


def evaluate_suite_strength(
    problem_id: str,
    reference_code: str,
    test_cases: List[dict],
    function_signature: str,
    difficulty: str = "medium",
) -> SuiteStrengthReport:
    """
    Evaluate how robust a test suite is under adversarial conditions.

    Steps:
        1. Verify reference solution passes E=1.0
        2. Generate mutations of the reference solution
        3. Run each mutated variant against the test suite
        4. Count how many mutations are "killed" (test catches the error)
        5. Generate adversarial tests (structurally, not from oracle)

    A high kill rate means the test suite catches most mutations.
    A low kill rate means the test suite is shallow.
    """
    if not reference_code:
        return SuiteStrengthReport(
            problem_id=problem_id,
            reference_pass=False,
            mutation_count=0,
            mutations_killed=0,
            mutation_kill_rate=0.0,
            adversarial_count=0,
            strength_score=0.0,
            details={"mutation_classes": [], "mutation_breakdown": {}},
        )

    mutation_engine = MutationEngine(problem_id, num_variants_per_class=3)
    adversarial_gen = AdversarialGenerator(problem_id, function_signature, difficulty)

    mutations = mutation_engine.generate_all(reference_code)
    adversarial_cases = adversarial_gen.generate()

    ref_pass = _run_solution(reference_code, test_cases) == 1.0

    mutations_killed = 0
    for mut in mutations:
        mut_rate = _run_solution(mut.mutated_code, test_cases)
        if mut_rate < 1.0:
            mutations_killed += 1

    kill_rate = mutations_killed / len(mutations) if mutations else 0.0
    adv_count = len([tc for tc in adversarial_cases if tc.input_data is not None])

    strength_score = kill_rate

    return SuiteStrengthReport(
        problem_id=problem_id,
        reference_pass=ref_pass,
        mutation_count=len(mutations),
        mutations_killed=mutations_killed,
        mutation_kill_rate=kill_rate,
        adversarial_count=adv_count,
        strength_score=strength_score,
        details={
            "mutation_classes": list(set(m.mutation_class for m in mutations)),
            "mutation_breakdown": _breakdown_by_class(mutations, test_cases),
        },
    )


def _run_solution(code: str, test_cases: List[dict]) -> float:
    """Run a solution against test cases. Returns pass rate."""
    try:
        from doctor.normalize.solution_normalizer import extract_function, normalize_solution
        from doctor.core.test_executor import run_test_with_trace, _results_equal

        normalized = normalize_solution(code)
        func = extract_function(normalized)
        if func is None:
            return 0.0

        passed = 0
        for tc in test_cases:
            trace = run_test_with_trace(func, tuple(tc["input"]), tc["expected"])
            if trace.get("error") is None and _results_equal(trace.get("output"), tc["expected"]):
                passed += 1

        return passed / len(test_cases) if test_cases else 0.0
    except Exception:
        return 0.0


def _breakdown_by_class(mutations: List[MutationResult], test_cases: List[dict]) -> Dict[str, dict]:
    """Show kill rate broken down by mutation class."""
    by_class: Dict[str, List[float]] = {}
    for m in mutations:
        by_class.setdefault(m.mutation_class, [])
        rate = _run_solution(m.mutated_code, test_cases)
        by_class[m.mutation_class].append(rate)

    return {
        cls: {
            "count": len(rates),
            "avg_pass_rate": sum(rates) / len(rates),
            "fully_killed": sum(1 for r in rates if r < 1.0),
        }
        for cls, rates in by_class.items()
    }


def format_report(report: SuiteStrengthReport) -> str:
    """Human-readable strength report."""
    lines = [
        f"=== Suite Strength Report: {report.problem_id} ===",
        f"Reference solution passes: {report.reference_pass}",
        f"",
        f"Mutation robustness:",
        f"  variants generated: {report.mutation_count}",
        f"  variants killed:   {report.mutations_killed}",
        f"  kill rate:         {report.mutation_kill_rate:.1%}",
        f"",
        f"Adversarial tests: {report.adversarial_count} cases generated",
        f"",
        f"Strength score: {report.strength_score:.2f}",
        f"",
        f"Breakdown by mutation class:",
    ]

    breakdown = report.details.get("mutation_breakdown", {})
    for cls, stats in breakdown.items():
        killed = stats["fully_killed"]
        total = stats["count"]
        rate = killed / total if total else 0
        lines.append(f"  {cls}: {killed}/{total} killed ({rate:.0%})")

    return "\n".join(lines)
