"""Run regime stability validation on 4 problems."""

from doctor.ingestion import TestCaseSpec
from doctor.test_executor import TEST_SUITES, PROBLEM_KEY_MAP
from doctor.regime_stability import compute_stability, format_stability_report

problem_constraints = {
    "two_sum": {"nums": {"min_length": 2}, "target": {"min": -10**9, "max": 10**9}},
    "solve_n_queens": {"n": {"min": 0, "max": 9}},
    "max_area": {"height": {"min_length": 2, "min": 0, "max": 10**5}},
    "valid_parentheses": {"s": {"min_length": 0, "max_length": 10000}},
}

for problem_key, constraints in problem_constraints.items():
    test_cases = TEST_SUITES.get(problem_key)
    if test_cases is None:
        continue

    specs = [TestCaseSpec(input=tc.input, expected=tc.expected, label=tc.label) for tc in test_cases]

    report = compute_stability(
        problem_id=problem_key,
        test_cases=specs,
        constraints=constraints,
    )

    print(format_stability_report(report))
    print("-" * 65)
    print()
