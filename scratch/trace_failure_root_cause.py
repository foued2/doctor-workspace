"""Trace exactly WHY failures happen — validator or comparison path?"""
from doctor.test_executor import _verify_with_validator, _results_equal, _build_validator_params

print("=" * 65)
print("TRACE 1: Two Sum partial (got=None on negative test)")
print("=" * 65)

# The negative_numbers test: input=([-1,-2,-3,-4,-5], -8), expected=[2,4]
test_input = ([-1, -2, -3, -4, -5], -8)
got = None  # partial solution skips negatives → returns None

# Step 1: What does the validator say?
validator_result, validator_kind = _verify_with_validator("Two Sum", got, test_input)
print(f"Validator result: {validator_result}")
print(f"Validator kind: {validator_kind}")

# If validator_kind == "validator_passed", the system treats it as valid
# even though got=None doesn't match expected=[2,4]
if validator_kind == "validator_passed":
    print("→ BUG: Validator passed None output!")
elif validator_kind == "validator_failed":
    print("→ Validator correctly rejected None")
else:
    # No validator — falls back to expected output
    equal = _results_equal(got, [2, 4])
    print(f"No validator. _results_equal(None, [2,4]) = {equal}")


print()
print("=" * 65)
print("TRACE 2: Container always-0 (got=0, expected=49)")
print("=" * 65)

test_input_c = ([1, 8, 6, 2, 5, 4, 8, 3, 7],)
got_c = 0

validator_result_c, validator_kind_c = _verify_with_validator("Container With Most Water", got_c, test_input_c)
print(f"Validator result: {validator_result_c}")
print(f"Validator kind: {validator_kind_c}")

if validator_kind_c == "validator_passed":
    print("→ BUG: Validator passed wrong answer (0 != 49)")
elif validator_kind_c == "validator_failed":
    print("→ Validator correctly rejected 0")
else:
    equal_c = _results_equal(got_c, 49)
    print(f"No validator. _results_equal(0, 49) = {equal_c}")


print()
print("=" * 65)
print("TRACE 3: Container always-999 (got=999, expected=49)")
print("=" * 65)

got_c2 = 999
validator_result_c2, validator_kind_c2 = _verify_with_validator("Container With Most Water", got_c2, test_input_c)
print(f"Validator result: {validator_result_c2}")
print(f"Validator kind: {validator_kind_c2}")

if validator_kind_c2 == "validator_passed":
    print("→ BUG: Validator passed wrong answer (999 != 49)")
elif validator_kind_c2 == "validator_failed":
    print("→ Validator correctly rejected 999")
else:
    equal_c2 = _results_equal(got_c2, 49)
    print(f"No validator. _results_equal(999, 49) = {equal_c2}")


print()
print("=" * 65)
print("ROOT CAUSE ANALYSIS")
print("=" * 65)
print("""
The system has a TWO-LEVEL verification path:
  Level 1: Problem-specific validator (validate_output)
  Level 2: Expected-output comparison (_results_equal)

If Level 1 exists and PASSES → output is valid, Level 2 is SKIPPED.
If Level 1 exists and FAILS → output is invalid.
If Level 1 doesn't exist → fall back to Level 2.

FAILURE 1b (Two Sum partial):
  The Two Sum validator (validate_output) is passing None output.
  This means the validator is BROKEN — it accepts None as valid indices.

FAILURE 3c/3d (Container always-0/always-999):
  The Container validator passes ANY non-negative integer (weak validator).
  But the test executor ALSO has expected-output comparison (Level 2).
  If the validator passes, Level 2 is SKIPPED entirely.
  So 0 and 999 both pass the weak validator → verdict=correct.

The structural flaw: When a validator exists (even a weak one),
it COMPLETELY BYPASSES expected-output comparison.
This is by design (Phase 2.5), but the design is WRONG for weak validators.
""")
