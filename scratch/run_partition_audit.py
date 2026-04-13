"""Run structural partition audit on all problems with reference solutions."""

from doctor.ingestion import TestCaseSpec
from doctor.test_executor import TEST_SUITES, PROBLEM_KEY_MAP
from doctor.structural_partition import audit_partition_coverage, format_partition_report

# ═══ Problem constraints ═══

problem_constraints = {
    "two_sum": {"nums": {"min_length": 2}, "target": {"min": -10**9, "max": 10**9}},
    "solve_n_queens": {"n": {"min": 0, "max": 9}},
    "max_area": {"height": {"min_length": 2, "min": 0, "max": 10**5}},
    "valid_parentheses": {"s": {"min_length": 0, "max_length": 10000}},
}

# ═══ Run audit on each problem with reference solution ═══

for problem_key, constraints in problem_constraints.items():
    test_cases = TEST_SUITES.get(problem_key)
    if test_cases is None:
        continue

    specs = [TestCaseSpec(input=tc.input, expected=tc.expected, label=tc.label) for tc in test_cases]

    report = audit_partition_coverage(
        problem_id=problem_key,
        test_cases=specs,
        constraints=constraints,
    )

    print(format_partition_report(report))
    print("-" * 65)
    print()
