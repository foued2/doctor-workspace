"""End-to-end validation: ingestion pipeline → grading engine."""

from doctor.ingestion import (
    parse_problem, approve_reference, TestCaseSpec,
    ingest_problem, to_test_cases,
)
from doctor.test_executor import TestExecutor, TEST_SUITES, PROBLEM_KEY_MAP

# ═══ Ingest Two Sum ═══

def two_sum_reference(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []

spec = parse_problem(
    problem_id="two_sum",
    display_name="Two Sum",
    description="Return indices of two numbers that add up to target.",
    input_schema={"nums": "list[int]", "target": "int"},
    output_type="list[int]",
    constraints={"nums": {"min_length": 2}, "target": {"min": -10**9, "max": 10**9}},
    reference_solution=two_sum_reference,
)
approve_reference(spec)

manual = [
    TestCaseSpec(([2, 7, 11, 15], 9), [0, 1], "basic", "manual"),
    TestCaseSpec(([3, 2, 4], 6), [1, 2], "no_first_two", "manual"),
    TestCaseSpec(([3, 3], 6), [0, 1], "self_element_reuse", "manual"),
    TestCaseSpec(([-1, -2, -3, -4, -5], -8), [2, 4], "negative_numbers", "manual"),
    TestCaseSpec(([1, 5, 3, 7], 10), [2, 3], "unsorted", "manual"),
]

boundaries = [
    ([1, 2], 3),
    ([10**9, -10**9], 0),
    ([0, 0], 0),
]

result = ingest_problem(spec, manual, boundaries)
print(f"Ingested Two Sum: {len(result.test_cases)} tests, hash={result.integrity_hash}")
assert len(result.validation_errors) == 0, f"Errors: {result.validation_errors}"

# ═══ Feed ingested tests through grading engine ═══

# Temporarily swap in ingested test suite
original_suite = TEST_SUITES["two_sum"]
ingested_test_cases = to_test_cases(result)
TEST_SUITES["two_sum"] = ingested_test_cases

correct_two_sum = (
    "def twoSum(nums, target):\n"
    "    seen = {}\n"
    "    for i, n in enumerate(nums):\n"
    "        if target - n in seen:\n"
    "            return [seen[target - n], i]\n"
    "        seen[n] = i"
)

incorrect_two_sum = (
    "def twoSum(nums, target):\n"
    "    for i, x in enumerate(nums):\n"
    "        if x + x == target: return [i, i]\n"
    "    return [0, 0]"
)

te = TestExecutor()

# Correct solution should pass ALL ingested tests
r_correct = te.verify("Two Sum", correct_two_sum)
print(f"\nCorrect solution: verdict={r_correct.verdict}, pass_rate={r_correct.pass_rate}, total={r_correct.total}")
assert r_correct.verdict == "correct", f"Correct solution got {r_correct.verdict}"
assert r_correct.pass_rate == 1.0, f"Correct solution pass_rate={r_correct.pass_rate}"

# Incorrect solution should fail
r_incorrect = te.verify("Two Sum", incorrect_two_sum)
print(f"Incorrect solution: verdict={r_incorrect.verdict}, pass_rate={r_incorrect.pass_rate}")
assert r_incorrect.verdict == "incorrect", f"Incorrect solution got {r_incorrect.verdict}"

# Container (no ingestion, verify unchanged)
r_container_wrong = te.verify("Container With Most Water", "def maxArea(h): return 0")
print(f"Container (wrong): verdict={r_container_wrong.verdict}, pass_rate={r_container_wrong.pass_rate}")
assert r_container_wrong.verdict == "incorrect", f"Container wrong got {r_container_wrong.verdict}"

# Restore original suite
TEST_SUITES["two_sum"] = original_suite

print("\nEnd-to-end validation PASSED ✓")
print(f"  - Correct solution: {r_correct.passed}/{r_correct.total} passed")
print(f"  - Incorrect solution: {r_incorrect.passed}/{r_incorrect.total} passed")
print(f"  - Container E-only oracle: {r_container_wrong.verdict}")
print(f"  - Ingestion pipeline did NOT touch grading logic")
