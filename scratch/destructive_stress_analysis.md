# DESTRUCTIVE STRESS TEST — ROOT CAUSE ANALYSIS

**Date:** 2026-04-13  
**Status:** 3 CRITICAL FAILURES DETECTED  
**Pass Rate:** 27/30 (90.0%)  

---

## SUMMARY

30 adversarial tests executed across 6 attack vectors. 27 passed, 3 CRITICAL failures found.

| Attack Vector | Tests | Failures | Severity |
|---|---|---|---|
| 1. E2E Correctness Bypass | 4 | 1 | CRITICAL |
| 2. Measurement Adversarial | 3 | 0 | — |
| 3. Validator Robustness | 4 | 2 | CRITICAL |
| 4. Reference Integrity | 12 | 0 | — |
| 5. Scaling Logic Stress | 4 | 0 | — |
| 6. Cross-Layer Consistency | 3 | 0 | — |

---

## CRITICAL FAILURE #1: Two Sum Validator Accepts `None` Output

**Test ID:** `1b E2E: Partial solution accepted as correct`

### Reproduction
```python
code = """
def twoSum(nums, target):
    h = {}
    for i,x in enumerate(nums):
        if x < 0: continue  # BUG: skips negative numbers
        if target-x in h: return [h[target-x],i]
        h[x]=i
"""
te.verify("Two Sum", code)  # → verdict=correct, pass_rate=1.0
```

### Root Cause
The Two Sum test suite includes a `negative_numbers` test: `input=([-1,-2,-3,-4,-5], -8), expected=[2,4]`.

The partial solution skips negative numbers (`if x < 0: continue`), so it never finds the pair. The function returns `None` (implicit Python return when no `return` statement executes).

The test executor then calls `_verify_with_validator("Two Sum", None, test_input)`. The Two Sum validator (`validate_output` with `verify_indices`) **passes** `None` as valid. This means the validator's `verify_indices` function does not reject `None` input.

Since the validator passes, the expected-output comparison (`_results_equal(None, [2,4])`) is **skipped entirely**.

### Structural Flaw
**Phase 2.5 design defect:** When a validator exists and passes, expected-output comparison is bypassed. If the validator is lenient (accepts `None`), wrong answers are accepted as correct.

### Layer
Layer 2 (Test Executor) → Validator bypass

### Deterministic
Yes — reproduces 100% of the time.

---

## CRITICAL FAILURE #2: Container Weak Validator Bypasses Expected Output

**Test ID:** `3c Validator: Weak validator false-accepts incorrect output`

### Reproduction
```python
code = "def maxArea(height): return 0"  # always wrong
te.verify("Container With Most Water", code)  # → verdict=correct, pass_rate=1.0
```

### Root Cause
Container's validator is **weak** — it only checks `area >= 0`. Any non-negative integer passes.

Since the validator exists and passes, the expected-output comparison (`_results_equal(0, 49)`) is **skipped entirely**.

The test suite has 4 test cases with expected outputs `[49, 1, 16, 2]`. The function returns `0` for all. `_results_equal(0, 49) = False` for every test. But the validator override means these comparisons never happen.

### Structural Flaw
**Same as Failure #1:** Phase 2.5 design bypasses expected-output comparison whenever a validator passes. Weak validators (which accept almost anything) effectively **disable the entire test execution layer**.

### Layer
Layer 2 (Test Executor) + Validator

### Deterministic
Yes — reproduces 100% of the time.

---

## CRITICAL FAILURE #3: Container Weak Validator Accepts Arbitrarily Wrong Answer

**Test ID:** `3d Validator: Weak validator + wrong answer accepted`

### Reproduction
```python
code = "def maxArea(height): return 999"  # wrong for all test cases
te.verify("Container With Most Water", code)  # → verdict=correct, pass_rate=1.0
```

### Root Cause
Identical to Failure #2. The weak validator accepts `999 >= 0`. Expected-output comparison is bypassed. All 4 tests "pass" because the validator says so.

### Structural Flaw
Same as Failures #1 and #2. The validator strength distinction is **cosmetic, not functional**. Weak validators behave identically to strong validators in the verification path — they both bypass expected-output comparison.

### Layer
Layer 2 (Test Executor)

### Deterministic
Yes — reproduces 100% of the time.

---

## COMMON ROOT CAUSE: Phase 2.5 Design Defect

All 3 failures share the same structural flaw:

```
if validator exists and passes:
    output = valid  # ← expected-output comparison SKIPPED
elif validator exists and fails:
    output = invalid
else:
    # fall back to expected-output comparison
    output = (got == expected)
```

The problem: **weak validators pass too easily, and when they do, expected-output comparison is never consulted**.

### The Fix Required
Weak validators should NOT bypass expected-output comparison. The verification path should be:

```
if validator is STRONG and passes:
    output = valid  # strong validator is sufficient
elif validator is STRONG and fails:
    output = invalid
elif validator is WEAK and passes:
    # weak validator passes → fall through to expected-output check
    output = (got == expected)
elif validator is WEAK and fails:
    output = invalid  # weak validator can reject
else:
    # no validator → fall back to expected-output comparison
    output = (got == expected)
```

---

## WHAT PASSED (27/30)

| Test | Result |
|---|---|
| Measurement stability (30 runs, no drift) | ✓ |
| Call order bias | ✓ |
| Noop overhead positive | ✓ |
| Strong validator accepts valid N-Queens | ✓ |
| Reference models: external=absolute+stable | ✓ |
| S_ref values reasonable | ✓ |
| Deterministic classification | ✓ |
| Reversed sizes rejected | ✓ |
| Constant S → slope≈0 | ✓ |
| Identical sizes → None | ✓ |
| Zero/negative inputs → None | ✓ |
| Correct slow solution: correct efficiency | ✓ |
| Container efficiency independent of validator | ✓ |
| Unknown problem handled gracefully | ✓ |

---

## CONCLUSION

The system is **structurally valid as a measurement system** (S-layer, scaling, references all work correctly). But it has a **critical design defect in Phase 2.5**: the validator override mechanism allows weak validators to bypass expected-output comparison, accepting wrong answers as correct.

This is NOT a measurement problem. It is a **verification path** problem.

**Recommendation:** Fix the verification path in `test_executor.py` to only bypass expected-output comparison for **strong** validators. Weak validators should still run but NOT override the expected-output check.

---

*Report generated: 2026-04-13*  
*Detailed data: scratch/destructive_stress_test_report.json*  
*Root cause trace: scratch/trace_failure_root_cause.py*
