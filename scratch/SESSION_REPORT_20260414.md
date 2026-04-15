# Session Report — 2026-04-14

## Summary

This session focused on: (1) fixing a critical logic bug in trust.py discovered during stress testing, (2) correcting the Phase 1 maturity assessment from binary pass/fail to a proper maturity model, and (3) implementing a trace-first evaluation loop that produces frozen artifacts for offline analysis.

---

## Changes Made

### 1. trust.py — v1.3 (Critical Fix)

**File:** `doctor/trust.py`

**Problem discovered:** Stress testing revealed the system could not detect "false justification" — cases where E=1 (correct output) but evidence is weak (e < 0.6) and model confidence is high (c >= 0.8). These were incorrectly classified as LOW risk.

**Fix applied:**
- Added `EVIDENCE_STRONG = 0.7` threshold for LOW classification
- Added explicit "false_justified_confidence" type for E=1, e<0.6, c>=0.8
- Added "aligned_but_weak_evidence" for aligned cases with weak evidence
- Enforced `type` as PRIMARY diagnosis, `risk` as SECONDARY severity bucket
- Added `_TYPE_TO_RISK` lookup table to ensure risk is always derived from type

**Before:**
```
E=1, e=0.2, c=0.9 → LOW (weak_alignment_correct)  [WRONG]
```

**After:**
```
E=1, e=0.2, c=0.9 → HIGH (false_justified_confidence)  [CORRECT]
```

**Decision contract now explicit:**
- PRIMARY = `type` (diagnosis, failure mode classification)
- SECONDARY = `risk` (severity bucket, for aggregation only)
- Trust layer CANNOT influence grading until Phase 3

---

### 2. Stress Test Framework

**File:** `tests/stress_test_trust.py`

**Added comprehensive stress testing:**
- Task 1: Full quadrant coverage (all 8 E/e/c combinations)
- Task 2: Distribution analysis (risk/type/counts, delta histogram)
- Task 3: Sensitivity test (±0.05 noise perturbation)
- Task 4: False justification probe (v1.1/v1.2 target)
- Task 5: Hierarchy check (type PRIMARY, risk SECONDARY)
- Task 6: Quadrant collapse check
- Task 7: Delta boundary analysis

**Verification results (v1.3):**
| Test | Result |
|------|--------|
| Quadrant coverage | 25 cases across all 8 combinations |
| Sensitivity | 0/6 cases flip with ±0.05 noise |
| False justification | 3/3 detected |
| Type→Risk derivation | 6/6 verification pairs pass |
| Distribution | LOW=20%, MEDIUM=32%, HIGH=24%, CRITICAL=24% |

---

### 3. Delta Analysis — Correction

**Files:** `tests/analyze_delta_results.py`, `scratch/DELTA_CORRECTION.md`, `scratch/delta_analysis_report.json`

**Initial incorrect claim:** "Delta = 71.4% = strong signal, proceed to Phase 2"

**Correction applied:**
- Claim was based on single-run experiment with no raw per-case data
- Cannot compute calibration error, bootstrap CI, or stability without raw traces
- P(correct|low)=0% in n=27 is statistically suspicious
- "0% low confidence accuracy" is often a red flag (sparsity, pathological thresholding)

**Corrected framing:**
> "Plausible but non-identifiable correlation artifact with missing observational structure"

**Phase 2 status: BLOCKED** until proper instrumentation exists.

---

### 4. Phase 1 Maturity Model

**Files:** `scratch/phase1_status.json`, `scratch/PHASE1_CLOSURE_CHECKLIST.md`, `session_state_20260414.md`

**Initial incorrect framing:** "Phase 1 = 0/24 criteria" (binary pass/fail)

**Correction applied:** Phase 1 is a maturity hierarchy, not binary gates:

| Level | Meaning | Status |
|-------|---------|--------|
| L1 Exists | Component runs | MOSTLY COMPLETE |
| L2 Observable | Outputs trace-logged | PARTIAL |
| L3 Stable | Behavior consistent across runs | NOT STARTED |
| L4 Robust | Survives adversarial stress | NOT STARTED |

**Phase 1 complete when:**
1. L1→L2: All components produce trace-logged outputs
2. L2→L3: One full run reproduced identically
3. L3→L4: Adversarial failure rate < threshold

---

### 5. Trace-First Evaluation Loop

**Files:** `tests/run_trace_first.py`, `tests/run_offline_analysis.py`

**Implemented:**
- Single entry point that executes adversarial suite + delta experiment
- Produces frozen artifact with full traces
- Per-case schema: input_id, case_name, E, evidence_score, confidence, correctness, timestamp
- Immutable artifact format for reproducibility

**Artifact produced:** `scratch/trace_first_artifact_20260414_202019.json`

**Results:**
- Adversarial suite: 7 cases, 3 failures (42.9%)
- Evidence scores: min=0.00, max=0.95, mean=0.65
- Delta experiment: Skipped (Ollama unavailable)
- Maturity: L2=YES, L3=UNKNOWN, L4=NO (failure rate too high)

---

## Files Created/Modified

### Created
| File | Purpose |
|------|---------|
| `doctor/trust.py` (modified) | v1.3 with explicit decision contract |
| `doctor/delta_experiment.py` | DeltaExperiment framework (needs numpy) |
| `tests/stress_test_trust.py` | Comprehensive stress testing |
| `tests/run_trace_first.py` | Trace-first evaluation loop |
| `tests/run_offline_analysis.py` | Offline analysis from artifact |
| `tests/analyze_delta_results.py` | Delta analysis runner |
| `scratch/PHASE1_CLOSURE_CHECKLIST.md` | Corrected maturity checklist |
| `scratch/phase1_status.json` | Machine-readable maturity model |
| `scratch/DELTA_CORRECTION.md` | Philosophical correction |
| `session_state_20260414.md` | Corrected session state |

### Modified
| File | Change |
|------|--------|
| `doctor/trust.py` | v1.1 → v1.2 → v1.3 (false justification fix, hierarchy) |
| `tests/mismatch_experiment.py` | Minor output formatting |

---

## Philosophical Corrections

1. **On delta experiment:**
   - OLD: "Strong signal, proceed to Phase 2"
   - NEW: "Plausible but non-identifiable artifact, Phase 2 blocked"

2. **On Phase 1 maturity:**
   - OLD: "0/24 criteria met"
   - NEW: "L1 mostly complete, L2 partial, L3/L4 not started"

3. **On trust.py:**
   - OLD: "type and risk are both used for decisions"
   - NEW: "type is PRIMARY, risk is derived for aggregation only"

4. **On validation:**
   - OLD: "Component existence = validation complete"
   - NEW: "Reproducible trace-logged outputs under controlled conditions"

---

## Current System State

```
Oracle:        L1=DONE  L2=PARTIAL  L3=UNKNOWN  L4=NO
Trace:         L1=PARTIAL L2=YES    L3=NO       L4=N/A
Confidence:    L1=DONE   L2=DONE    L3=NO       L4=NO
Phase gate:    L1=DONE   L2=PARTIAL L3=NO       L4=NO
```

```
Phase 2: BLOCKED
  - Need: Ollama for delta experiment
  - Need: Replayability verification
  - Need: Adversarial suite ≥100 cases
```

---

## Key Insight

The session revealed that the system has **construction maturity** but not **empirical maturity**. Components exist and produce outputs, but:
- Outputs are not trace-logged in unified schema
- Experiments are not reproducible
- Statistical characterization is missing

**Next step:** Execute trace-first loop with Ollama, verify replayability, then assess Phase 1 closure.
