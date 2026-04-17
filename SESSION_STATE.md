# Doctor Workspace - Session State (Updated 2026-04-17)

## Current Goal

Stabilization Phase: Make Doctor reliably runnable so problem-solving dominates activity.
Target: ~60-70% problem reasoning (vs ~5% before).

## Tier 1-2 Stabilization (COMPLETED)

### Priority 1 — Execution Contract ✅

| File | Changes |
|------|---------|
| `doctor/adversarial/mutation_evaluator.py` | `ExecutionState` enum (OK/WRONG/TIMEOUT/ERROR). Every evaluation returns exactly one state. `ExecutionResult` (frozen), `ExecutionSummary` (structured). |

Guarantee: No `None` returns. No mixed states. Clear `is_ok/is_wrong/is_timeout/is_error` methods.

### Priority 2 — Normalizer Subset Enforcement ✅

| File | Changes |
|------|---------|
| `doctor/normalize/solution_normalizer.py` | `NormalizationError` on unsupported constructs. Validates BEFORE transformation (fast fail). Rejects walrus `:=`, async/await, `@overload`, Protocol classes, complex default args. |

### Priority 3 — `_to_test_input` Cleanup ✅

| File | Changes |
|------|---------|
| `doctor/core/test_executor.py` | Removed recursive calls. Simple explicit logic. Special case only for `merge_two_sorted_lists` (ListNode conversion). |

### Priority 4 — Mutation Preflight ✅

Filters applied in `_filter_effective_mutations`:
1. **DISCARD** if times out on ALL canonical inputs (infinite loop)
2. **DISCARD** if output identical to reference on ALL inputs (no-op)
3. **DEDUPLICATE** by output signature → keep first representative

### Priority 5 — Auto-Registration ✅

| File | Changes |
|------|---------|
| `doctor/adversarial/mutation_engine.py` | `MUTATION_CLASSES` derived from `_init_mutators()` keys. `_init_mutators()` called at module load. No hardcoded list. |

Adding a new mutator class is now sufficient. No separate list to update.

### Priority 6 — Mutation Result Classification ✅

Breakdown includes `by_state` dict: OK/WRONG/TIMEOUT/ERROR counts per class.

### Priority 7 — Full Failure Mapping ✅

`ExecutionSummary.failing_tests`: list of `{label, input, expected, failure_state, got}` for every failed test case.

### Priority 9 — Metric Clarity ✅

Benchmark shows `effective/raw` per problem (e.g., `6/12` = 6 effective of 12 raw).
Format report shows explicit redundancy percentage.

## Benchmark Results (Final)

```
Problems:              32
With references:       11
Raw mutations:        106
Effective mutations:   34
Duplication rate:     68%
Average kill rate:   100%
```

| Problem                     | Eff/Raw | Kill% |
|----------------------------|---------|-------|
| Multiples of 3 and 5      | 6/12    | 100%  |
| Even Fibonacci Numbers      | 3/9     | 100%  |
| Largest Prime Factor       | 2/6     | 100%  |
| Generate Parentheses       | 4/14    | 100%  |
| 3Sum                      | 7/19    | 100%  |
| N-Queens                  | 3/11    | 100%  |

## Remaining Pain Points

1. **Test contribution = 0 for all tests** — suite has redundancy but we don't know which tests cover the same failure modes
2. **Mutation classes are domain-specific** — `arithmetic_perturbation` fires 0 effective mutations (always no-ops after filter)
3. **No systematic test design** — inputs chosen manually, no bug-pattern-to-test mapping
4. **No pipeline command** — running ingest → benchmark → report requires separate steps

## Tier 3 Visibility (NEXT — Not Started)

- Priority 7: Pipeline command (`python -m doctor.pipeline --problem euler_3`)
- Priority 8: Failure clustering ("mutations A,B,C all fail on prime inputs")
- Priority 11: Test suite intelligence (detect redundant tests, suggest missing cases)

## Tier 4 Controlled Improvements (Future)

- Priority 10: Mutation context awareness (loop/return/arithmetic restrictions)
- Priority 11: Test suite design tool (auto-generate from bug patterns)

## Key Files

| Component | File | Status |
|-----------|------|--------|
| Normalizer | `doctor/normalize/solution_normalizer.py` | ✅ Hardened with subset validation |
| Test Executor | `doctor/core/test_executor.py` | ✅ `_to_test_input` simplified |
| Mutation Engine | `doctor/adversarial/mutation_engine.py` | ✅ Auto-registration, sign_flip fixed |
| Mutation Evaluator | `doctor/adversarial/mutation_evaluator.py` | ✅ Execution contract, prefilters, failure mapping |
| Benchmark | `doctor/benchmark/benchmark.py` | ✅ Uses ExecutionState, shows eff/raw |
| Registry | `doctor/registry/problem_registry.json` | 32 problems, 11 with references |

## Commits (This Session)

- `bbb3cc1`: Add timeout protection, fix precision_degradation infinite loop, add euler_2 and euler_3
- `89858c0`: Semantic mutation filtering, deduplication, test contribution analysis
- `64df1a3`: Tier 1-2 Stabilization: execution contract, normalizer hardening, auto-registration
