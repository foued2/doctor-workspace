"""Debug the three critical failures."""
from doctor.test_executor import TestExecutor

te = TestExecutor()

# ── Failure 1b: Partial solution accepted as correct ──
print("=" * 65)
print("FAILURE 1b: Partial solution (skips negatives) accepted as correct")
print("=" * 65)
partial = (
    "def twoSum(nums, target):\n"
    "    h = {}\n"
    "    for i,x in enumerate(nums):\n"
    "        if x < 0: continue  # skip negatives — bug\n"
    "        if target-x in h: return [h[target-x],i]\n"
    "        h[x]=i"
)
r = te.verify("Two Sum", partial)
print(f"Verdict: {r.verdict}")
print(f"Pass rate: {r.pass_rate}")
print(f"Passed: {r.passed}/{r.total}")
print()
print("Per-test results:")
for res in r.results:
    print(f"  {res.label}: passed={res.passed}, got={res.got}, expected={res.expected}")
print()
print("TEST SUITE for Two Sum:")
from doctor.test_executor import TEST_SUITES
for tc in TEST_SUITES["two_sum"]:
    print(f"  {tc.label}: input={tc.input}, expected={tc.expected}")

# The key question: does the test suite include negative number tests?
# If not, the partial solution passes all tests despite being buggy.
has_negative_test = any("negative" in tc.label.lower() for tc in TEST_SUITES["two_sum"])
print(f"\nHas negative number test: {has_negative_test}")


# ── Failure 3c/3d: Container always-0 and always-999 accepted as correct ──
print()
print("=" * 65)
print("FAILURE 3c/3d: Container always-0/always-999 accepted as correct")
print("=" * 65)

for code, name in [
    ("def maxArea(height):\n    return 0", "always-0"),
    ("def maxArea(height):\n    return 999", "always-999"),
]:
    print(f"\n--- {name} ---")
    r2 = te.verify("Container With Most Water", code)
    print(f"Verdict: {r2.verdict}")
    print(f"Pass rate: {r2.pass_rate}")
    print(f"Passed: {r2.passed}/{r2.total}")
    print()
    print("Per-test results:")
    for res in r2.results:
        print(f"  {res.label}: passed={res.passed}, got={res.got}, expected={res.expected}")

print()
print("TEST SUITE for Container:")
for tc in TEST_SUITES["max_area"]:
    print(f"  {tc.label}: input={tc.input}, expected={tc.expected}")

# Check: does the test executor comparison function work correctly?
print()
print("Checking _results_equal behavior:")
from doctor.test_executor import _results_equal
for expected in [49, 1, 16, 2]:
    print(f"  _results_equal(0, {expected}) = {_results_equal(0, expected)}")
    print(f"  _results_equal(999, {expected}) = {_results_equal(999, expected)}")
