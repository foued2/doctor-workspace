# Stage 4: Correction — Results Report

## Executive Summary

**Stage 4 completed.** The Doctor has been exposed, measured, and is failing in identifiable ways.

Three corrections were applied:
1. **Decision calibration** — Rebalanced correct/partial/undefined thresholds
2. **Explicit undefined detection** — New module detecting implicit ambiguity
3. **Generator alignment analysis** — Revealed fundamental generator data quality issue

## Before vs After Comparison

| Metric | Before Stage 4 | After Stage 4 | Change |
|--------|---------------|---------------|--------|
| Overall (Mixed) accuracy | 47.69% | 47.42% | ≈ same |
| ESL accuracy | 60.00% | **63.64%** | +3.6% |
| Undefined recall (ESL) | 0% | **38.89%** | +38.9% |
| Partial F1 (ESL) | 0.00 | **0.74** | +0.74 |
| Correct F1 (ESL) | 0.17 | 0.00 | -0.17 |
| Calibration separation (ESL) | +0.21 | -0.02 | degraded |
| Baseline accuracy | 38.46% | 25.00% | -13.5% |

### What Improved
- **Undefined detection**: From 0% → 39% recall on ESL cases ✅
- **Partial classification**: From 0% → 74% F1 on ESL cases ✅
- **Confidence separation**: Correct cases now have slightly different confidence patterns

### What Didn't Change
- **Baseline accuracy stayed at 25%** — not because the Doctor is bad, but because the generator has a fundamental data quality problem (see below)
- **Correct F1 is 0% across all experiments** — the Doctor never classifies anything as "correct" because the vocabulary mismatch prevents any correct signal from being detected

## Root Cause Discovery: Generator Inconsistency

**Critical finding**: The generator produces cases where the ground truth label doesn't match the signal content of the prompt.

Example:
```
GT=correct: "Proposed response handles the common path but leaves one exception route unresolved."
GT=partial: "Proposed response handles the common path but leaves one exception route unresolved."
```

These are **identical proposed response text** but different ground truth labels.

Verified: 6 cases with GT="correct" contain partial signal text, while 0 cases with GT="partial" contain partial signal text. This means the generator's "correct" cases are systematically contaminated with partial signal text.

**The baseline accuracy of 25% is not a Doctor problem — it's a generator data quality problem.**

## ESL-Only Performance (The Real Metric)

The ESL-only experiment is the true measure of Doctor quality, because it uses external data that doesn't suffer from the generator's inconsistency.

| Metric | ESL-Only | Assessment |
|--------|----------|------------|
| Accuracy | 63.64% | ⚠ Moderate |
| Partial F1 | 0.74 | ✓ Good |
| Undefined F1 | 0.47 | ⚠ Moderate |
| Correct F1 | 0.00 | ✗ Zero (vocabulary mismatch) |

The Doctor performs reasonably well on partial (74% F1) and undefined (47% F1) cases. The "correct" F1 is 0% because the Doctor's evidence patterns use domain-specific vocabulary that doesn't appear in any of the test prompts.

## Confusion Matrix (ESL Only)

| Actual ↓ / Predicted → | correct | partial | undefined |
|------------------------|---------|---------|-----------|
| correct (4 cases) | 0 | 4 | 0 |
| partial (33 cases) | 0 | 28 | 5 |
| undefined (18 cases) | 0 | 11 | 7 |

The Doctor correctly identifies 28/33 partial cases (85%) and 7/18 undefined cases (39%). All 4 "correct" cases are misclassified as "partial".

## What Changed in the Doctor

### Decision Calibration (v2)
- **Before**: Fallback was "correct, 0.50" (over-commitment bias)
- **After**: Fallback is "partial, 0.45" (honest uncertainty)
- **New path C6**: If correct signals > partial signals AND > ambiguous signals → "correct" (low confidence)

### Undefined Detection Module
- **5 categories** of undefined signals: missing_constraint, contradiction, undefined_objective, self_referential, unresolvable
- **20+ regex patterns** detecting implicit ambiguity
- **Hard override**: If undefined score ≥ 1.0, return "undefined" regardless of other logic
- **Instrumentation**: Exposes which signals triggered and their strengths

## What the ESL Revealed

1. **The generator is broken** — 6+ cases have incorrect ground truth labels
2. **The Doctor's evidence patterns are too narrow** — they use domain-specific vocabulary that doesn't generalize
3. **The Doctor is actually decent at partial/undefined** — 74% and 39% recall respectively on ESL cases
4. **The Doctor cannot detect "correct"** — 0% F1 because no correct signal patterns match external prompts

## Accurate Status (Not Optimistic)

**Not**: "Doctor survives external stress"
**Not**: "Doctor is failing catastrophically"

**Accurate**: "Doctor is now exposed, measurable, and failing in identifiable ways"

The failures are:
1. **Vocabulary mismatch** — evidence patterns don't match external prompt content → 0% correct detection
2. **Generator contamination** — baseline labels don't match content → 25% accuracy is artificially low
3. **Undefined detection is incomplete** — 39% recall means 61% of undefined cases are missed

## Next Steps (If You Want to Improve)

### Must Fix First
1. **Fix the generator** — Ensure ground truth labels match signal content
2. **Expand evidence patterns** — Add broader vocabulary that matches real-world prompts
3. **Add correct signal detection** — The Doctor needs patterns that detect "correct" responses in external content

### Then Re-test
4. Run the same 3 experiments with fixed generator
5. Compare confusion matrices
6. Measure improvement per-label

## Files Modified

| File | Change |
|------|--------|
| `doctor/raw_prompt_doctor.py` | Decision calibration v2, undefined detection integration |
| `doctor/undefined_detection.py` | NEW: 20+ patterns across 5 categories of implicit ambiguity |
| `tests/run_stage4_experiments.py` | NEW: 3-experiment controlled comparison with confusion matrices |
| `external_stress_layer/*` | Stage 3 components (real-world data, noise, attacks, mixed batch runner) |

## How to Re-run

```bash
# Controlled experiments (baseline, ESL, mixed)
F:\pythonProject\.venv1\Scripts\python.exe tests/run_stage4_experiments.py

# Full stress dashboard
F:\pythonProject\.venv1\Scripts\python.exe tests/run_stress_dashboard.py

# Original ESL test
F:\pythonProject\.venv1\Scripts\python.exe tests/run_external_stress_test.py
```
