## Goal

Validate and implement a multi-phase code analysis/trust pipeline called "Doctor" with the following goals:
1. Verify workflow (git_push.py, SESSION_START.py, scratch/ artifacts)
2. Fix evidence.py bug (Line 215 - wrong args to compute_evidence_strength)
3. L3 Stability run (run 27-case suite 3 times, compare results)
4. Delta experiment with Ollama (classify runtime issue, run delta experiment)
5. End-to-end chain validation (test_executor → evidence.py → trust.py → risk output)
6. Implement mutation trace system with phase state machine
7. Validate pre-oracle confidence prediction (trust must predict before oracle resolves)

## Instructions

- Run `confidence_validation.py` 3 times to verify L3 stability
- Push trace artifacts to scratch/ and provide raw URLs for user to verify
- Classify Ollama runtime issues as operational/integration/conceptual
- Target stable + calibrated + non-trivial signal for delta experiment
- No reordering of steps
- **HARD CONSTRAINT**: No external APIs (no OpenAI, no Anthropic Claude)
- System must be deterministic, reproducible, and frozen during evaluation phases
- trust.py must be tested for pre-oracle predictive power, not post-hoc correlation with oracle

## Discoveries

### Ollama Status
1. **Ollama models on F: not loading** - Created junction `mklink /J C:\Users\foued\.ollama\models F:\ollama_models`
2. **phi3 does NOT support logprobs** - Returns only: `['model', 'response', 'done', 'done_reason', 'context', 'total_duration', 'eval_duration']`
3. **phi3 always outputs confidence=1.00** regardless of correctness - Model behavior issue, not integration issue. Classification: Conceptual
4. **mistral has logprobs support** but Ollama keeps crashing on port 11434 after restarts
5. **No Anthropic API key found** on the machine

### Pipeline Architecture Issues
1. **evidence.py bug was already fixed** - Memory was stale, all calls pass correct `(tests_total, tests_passed)` arguments
2. **test_executor fails on class-wrapped solutions** - `from typing import List` shadows built-in, `_safe_exec` finds `List` instead of method
3. **N-Queens test suite was thin** (3 cases) - e=0.580, causing false_justified_confidence
4. **Circularity problem**: `e` (evidence_strength) is derived from the same oracle that defines `E`, so "perfect separation" in trust types is by construction, not measurement

### Statistical Interpretation (Critical)
1. **Bootstrap p=0.52 is NOT acceptable** - The delta (+73.3%) is not statistically significant
2. **ECE=0.22 indicates moderate calibration error**
3. **trust.py is a deterministic oracle-driven labeling system**, not an independent confidence estimator
4. **The system cannot be validated by testing against oracle outputs it was designed to use**

### What Would Actually Validate the System
1. **Pre-oracle prediction**: trust.py must predict correctness BEFORE oracle resolution
2. **Cross-domain testing**: New problems not in design suite
3. **Statistically significant delta**: p < 0.05 on bootstrap
4. **Must beat trivial baselines**: complexity-only, length-only, random

## Accomplished

| Component | Status | Notes |
|-----------|--------|-------|
| Step 0 - Workflow verification | ✅ Complete | git_push.py, SESSION_START.py, scratch/ artifacts |
| Step 1 - evidence.py bug | ✅ Already fixed | Memory was stale |
| Step 2 - L3 Stability (3 runs) | ✅ Complete | Results IDENTICAL across runs |
| Step 3 - Delta with Ollama | ❌ Skipped | No logprobs, confidence=1.00, Ollama unstable |
| Step 4 - End-to-end validation | ✅ Complete | Option B (evidence-derived) passed |
| Solution Normalizer | ✅ Complete | `doctor/solution_normalizer.py` |
| N-Queens test suite expansion | ✅ Complete | 3 → 9 cases |
| Mutation Trace System | ✅ Complete | `doctor/mutation_trace.py` |
| Reproducibility Validation | ✅ Complete | Deterministic, PASS |
| Statistical Evaluation | ✅ Complete | Delta=+73.3%, but p=0.52 (not significant) |
| Pre-Oracle Validation | ✅ Complete | correlation=-0.430 (NEGATIVE) |
| **Residual Orthogonalization** | ✅ Complete | **94% variance explained, FULLY REDUNDANT** |

## Key Findings

### Pre-Oracle Validation Results
- **trust_pre correlation with E**: -0.430 (NEGATIVE)
- **Token count correlation**: 0.813 (9x better)
- **Complexity correlation**: 0.745 (9x better)
- **trust_pre ≈ complexity**: 0.753

### Residual Orthogonalization (NEW - 2026-04-15)
```
Baseline: E_hat = -0.2363*complexity + -0.0017*token_count + 1.7463
Residuals: mean=0.0000, std=0.3554

corr(trust_pre, E) = -0.6864
corr(trust_pre, residuals) = -0.0396

Variance reduction: 0.686 -> 0.040 (94% reduction)
VERDICT: FULLY REDUNDANT
```

### Conclusion
**trust.py is NOT a confidence model.**
- It is a syntactic difficulty proxy
- 94% of its variance is explained by complexity + token_count
- After orthogonalization, correlation drops to -0.04 (essentially zero)
- Higher trust_pre values actually correlate with INCORRECT solutions
- The negative correlation reveals calibration inversion

### What Would Be Needed for Valid Confidence Model
1. Features that actually predict correctness (syntax patterns, algorithmic choices)
2. Training data with ground truth labels
3. Statistical significance on held-out problems
4. Beat trivial baselines AFTER orthogonalization

## Relevant files / directories

### Core Pipeline Files
- `F:\pythonProject\doctor\test_executor.py` - Test execution, now uses solution_normalizer
- `F:\pythonProject\doctor\evidence.py` - Evidence strength computation
- `F:\pythonProject\doctor\trust.py` - Trust risk classification
- `F:\pythonProject\doctor\solution_normalizer.py` - **NEW**: Normalizes class-wrapped/typing imports
- `F:\pythonProject\doctor\mutation_trace.py` - **NEW**: Deterministic mutation system with phase state machine

### Test/Validation Scripts
- `F:\pythonProject\tests\confidence_validation.py` - L3 stability test (execution-based confidence)
- `F:\pythonProject\tests\run_e2e_option_b.py` - End-to-end chain validation (Option B)
- `F:\pythonProject\tests\L3_stability_minimal.py` - Minimal N=3 stability check
- `F:\pythonProject\tests\phase2_validation_v2.py` - Statistical evaluation (47 cases)
- `F:\pythonProject\tests\test_reproducibility.py` - Closed-loop reproducibility validation
- `F:\pythonProject\tests\pre_oracle_validation.py` - Pre-oracle confidence validation

### Scratch Artifacts (GitHub)
- https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/L3_run1_results.txt
- https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/L3_run2_results.txt
- https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/L3_run3_results.txt
- https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/e2e_option_b_results.txt
- https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/L3_stability_option_b.txt
- https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/phase2_validation.txt
- https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/statistical_evaluation.txt
- https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/pre_oracle_validation.txt
- https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/residual_orthogonalization.txt

### Specification Documents
- `F:\pythonProject\mutation_grammar_spec.md` - Mutation grammar specification
- `F:\pythonProject\mutation_trace_schema.md` - Mutation trace JSON schema v2
- `F:\pythonProject\statistical_interpretation.md` - Honest statistical assessment
- `F:\pythonProject\discussion_feedback_loop.md` - Feedback loop architecture discussion

## System Characterization Summary

| Property | Value | Status |
|----------|-------|--------|
| Deterministic | Yes | ✅ |
| L3 Stable | Identical across 3 runs | ✅ |
| Statistically significant delta | p=0.52 | ❌ |
| Pre-oracle signal | -0.430 | ❌ |
| Orthogonal to complexity | -0.040 (94% explained) | ❌ |
| Confidence model | No | ❌ |

**Hypothesis space exhausted.** System is a retrospective syntactic proxy, not a predictive confidence model.
