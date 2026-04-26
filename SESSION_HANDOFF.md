# Session Handoff — April 26 2026

## Branch: phase2-perturbation

---

# MASTER PROGRESS SUMMARY

## Era 1: LeetCode Learning System (DEPRECATED)

The original learning system with Suggestor + Doctor for practicing LeetCode problems.

- **Location**: `leetcode-tools/`
- **Status**: Deprecated, but still functional
- **Run**: `python leetcode-tools/leetcode_suggestor.py`

---

## Era 2: Doctor Grading System (Phase A & B — COMPLETE)

Fixed extraction and checker gaps for improved accuracy.

| Metric | Before | After |
|--------|--------|-------|
| Undefined Recall | 52.9% | 100.0% |
| Correct F1 | 0.0% | 88.0% |
| Wrong@HighConf | 7.8% | 37.0% |

**Key files:**
- `doctor/grading/doctor_grader.py` — Core grading
- `doctor/grading/trust.py` — Trust scoring
- `doctor/grading/evidence.py` — Evidence extraction
- `docs/production_report_phase_ab.md` — Full report

---

## Era 3: Tier 1-2 Stabilization (COMPLETE)

Nine stabilization priorities implemented.

| Priority | Component | Status |
|----------|-----------|--------|
| P1 | Execution Contract (`ExecutionState` enum) | ✅ |
| P2 | Normalizer Hardening | ✅ |
| P3 | `_to_test_input` Cleanup | ✅ |
| P4 | Mutation Prefilters | ✅ |
| P5 | Auto-Registration | ✅ |
| P6 | Mutation Result Classification | ✅ |
| P7 | Full Failure Mapping | ✅ |
| P9 | Metric Clarity | ✅ |

**Benchmark Results:**
- 32 problems, 34/106 effective mutations
- 68% duplication rate, 100% kill rate

**Key files:**
- `doctor/adversarial/mutation_evaluator.py`
- `doctor/normalize/solution_normalizer.py`
- `SESSION_STATE.md` — Full details

---

## Era 4: Phase 4 — Decision Contract (IMPLEMENTED)

Full formal decision contract with 8 items now mostly complete.

### The Decision Contract
```
Accept ⟺
  ¬contradiction
  ∧ ¬structural_modifier
  ∧ (objective_match ≥ T₁)
  ∧ (constraint_consistency ≥ T₂)
  ∧ (structural_compatibility ≥ T₃)
  ∧ (json_repair → alignment ≥ 0.90)
  ∧ match_candidate ∈ registry
```

### Phase 4 Items

| Item | Description | Status |
|------|-------------|--------|
| 1 | Adversarial Baseline Measurement | ✅ Done |
| 2 | Boundary Formalization | ✅ Done |
| 3 | Alignment Signal Validation | ✅ Done |
| 4 | Calibration | ✅ Done |
| 5 | Unified Validation | ✅ Done |
| 6 | OOD Detection via Embedding | NOT YET |
| 7 | Retry Tracking | ✅ Done |
| 8 | Reject Rate Monitoring | ✅ Done |

**Calibration Thresholds (frozen):**
- T₁ = 0.85 (alignment)
- T₂ = 0.7 (constraint_consistency)
- T₃ = 0.7 (structural_compatibility)

**Boundary Policy**: `docs/doctor_boundary_policy.md`
- Explicit inclusion/exclusion lists
- Collision surfaces (product vs sum, LCS vs LIS, etc.)
- Domain disguise rules

**Key files:**
- `docs/doctor_phase4_spec.md` — Full spec
- `docs/doctor_boundary_policy.md` — Policy rules
- `phase4_batch3_results.json` — Adversarial batch (12/12 correct)

---

## Era 5: Direction 2 — Dynamic Extraction (COMPLETE)

Dynamic problem extraction pipeline (NO REGISTRY NEEDED).

### Pipeline Flow
```
Problem Statement 
  ↓ (LLM extraction)
Schema (input/output, constraints, invariants, samples)
  ↓ (LLM generation)  
Checker (Python validator function)
  ↓ (protocol tests)
Evaluation with provisional confidence
```

### Components

| Component | Path | Status |
|-----------|------|--------|
| Extraction | `doctor/dynamic/extractor.py` | ✅ |
| Checker Generator | `doctor/dynamic/checker_generator.py` | ✅ |
| Pipeline | `doctor/dynamic/pipeline.py` | ✅ |
| Candidate Executor | `doctor/dynamic/candidate_executor.py` | ✅ |
| Test Schema | `doctor/dynamic/test_schemas/two_sum_schema.json` | ✅ |

### Checker Protocol (4 tests required)

1. **Sample validation** — All samples must pass
2. **Invariant enforcement** — Must reject known violations
3. **Negative testing** — Must reject wrong outputs
4. **Logic coverage** — Must reject each condition

### Confidence Rules

- Provisional mode max: MEDIUM (never HIGH)
- Trust ceiling: weakly_supported_correct
- Minimum RISK: MEDIUM

---

## Architecture (CURRENT)

### Entry Point
- `doctor/run_doctor.py` → `run_doctor(statement, solution_code) -> dict`

### Authoritative Path
- `unified_engine → solution_normalizer → test_executor → confidence_calibrator → trust`
- Uses registry test suites
- Full trust computation with evidence

### Experimental/Provisional Path
- `experimental/dynamic/pipeline.py` — provisional evaluator
- No registry needed, generates checker from schema
- Separate verdict namespace (`verdict: pending_execution`)

### Offline
- `offline/reject_monitor.py` — batch analytics

### Archive
- `archive/doctor_legacy.py` — old gate orchestrator (deprecated)

---

## Key Files Map

| Component | Path |
|-----------|------|
| Session State | `SESSION_STATE.md` |
| Phase A/B Report | `docs/production_report_phase_ab.md` |
| Phase 4 Spec | `docs/doctor_phase4_spec.md` |
| Boundary Policy | `docs/doctor_boundary_policy.md` |
| Run Doctor | `doctor/run_doctor.py` |
| Unified Engine | `doctor/ingest/unified_engine.py` |
| Trust | `doctor/grading/trust.py` |
| Calibration | `doctor/grading/confidence_calibrator.py` |
| Dynamic Pipeline | `experimental/dynamic/pipeline.py` |
| Dynamic Extractor | `doctor/dynamic/extractor.py` |
| Dynamic Checker Gen | `doctor/dynamic/checker_generator.py` |

---

## What Was Done This Session

- Direction 2 provisional path built and tested end-to-end (Tasks 3, 4, 5)
- Phase 4 Items 7 and 8 shipped (retry tracking, reject rate monitoring)
- Adversarial batch run (12/12 correct)
- Calibration thresholds validated and frozen
- `unified_engine.py` patched to log sub-scores on all reject paths
- `doctor/run_doctor.py` built as single authoritative entry point
- `reject_monitor.py` moved to `offline/`

---

## What Is Next

- Item 6 — OOD Detection via Embedding is the only remaining Phase 4 item
- `strong_underconfidence` trust type appearing on correct solutions is expected behavior with `c=0.5` neutral prior — not a bug

---

## Session Start Checklist

1. Read this file (`SESSION_HANDOFF.md`)
2. Check `SESSION_STATE.md` for Era 3 details
3. Run command from `session_init.md` if needed
4. Continue current task