"""Run sensitivity analysis on all existing TEST_SUITES."""

from doctor.ingestion import (
    parse_problem, approve_reference, TestCaseSpec,
)
from doctor.test_executor import TEST_SUITES, PROBLEM_KEY_MAP
from doctor.adversarial_coverage import (
    generate_sensitivity_report, format_report, compute_structural_coverage,
)

# ═══ Define reference solutions (human-approved, single-source) ═══

def two_sum_ref(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []

def nqueens_ref(n):
    res = []
    def bt(r, cols):
        if r == n:
            res.append(['.' * c + 'Q' + '.' * (n - c - 1) for c in cols])
            return
        for c in range(n):
            if all(c != cc and abs(r - i) != abs(c - cc) for i, cc in enumerate(cols)):
                bt(r + 1, cols + [c])
    bt(0, [])
    return res

def max_area_ref(height):
    left, right = 0, len(height) - 1
    max_a = 0
    while left < right:
        a = min(height[left], height[right]) * (right - left)
        max_a = max(max_a, a)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_a

def valid_parens_ref(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for c in s:
        if c in mapping:
            if not stack or stack[-1] != mapping[c]:
                return False
            stack.pop()
        else:
            stack.append(c)
    return len(stack) == 0

# ═══ Problem specs with references ═══

problem_refs = {
    "two_sum": {
        "ref": two_sum_ref,
        "constraints": {"nums": {"min_length": 2}, "target": {"min": -10**9, "max": 10**9}},
    },
    "solve_n_queens": {
        "ref": nqueens_ref,
        "constraints": {"n": {"min": 0, "max": 9}},
    },
    "max_area": {
        "ref": max_area_ref,
        "constraints": {"height": {"min_length": 2, "min": 0, "max": 10**5}},
    },
    "valid_parentheses": {
        "ref": valid_parens_ref,
        "constraints": {"s": {"min_length": 0, "max_length": 10000}},
    },
}

# ═══ Convert TEST_SUITES entries to TestCaseSpec format ═══

for problem_key, test_cases in TEST_SUITES.items():
    problem_name = next((k for k, v in PROBLEM_KEY_MAP.items() if v == problem_key), problem_key)
    ref_info = problem_refs.get(problem_key)

    if ref_info is None:
        continue  # No reference available yet

    specs = []
    for tc in test_cases:
        specs.append(TestCaseSpec(
            input=tc.input,
            expected=tc.expected,
            label=tc.label,
        ))

    # Run sensitivity analysis
    report = generate_sensitivity_report(
        problem_id=problem_key,
        test_cases=specs,
        reference_fn=ref_info["ref"],
        constraints=ref_info["constraints"],
        mutation_count=10,
    )

    print(format_report(report))
    print()
    print("-" * 65)
    print()
