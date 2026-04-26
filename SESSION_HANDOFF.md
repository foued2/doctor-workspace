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

## Era 4: Phase 4 — Decision Contract (SPEC COMPLETE)

Full formal decision contract with 8 items.

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
|------|-----------|--------|
| 1 | Adversarial Baseline Measurement | 📋 Done |
| 2 | Boundary Formalization | 📋 Done |
| 3 | Alignment Signal Validation | 📋 Done |
| 4 | Calibration | 📋 NOT YET |
| 5 | Unified Validation | 📋 Done |
| 6 | OOD Detection via Embedding | 📋 NOT YET |
| 7 | Retry Tracking | 📋 NOT YET |
| 8 | Reject Rate Monitoring | 📋 NOT YET |

**Boundary Policy**: `docs/doctor_boundary_policy.md`
- Explicit inclusion/exclusion lists
- Collision surfaces (product vs sum, LCS vs LIS, etc.)
- Domain disguise rules

**Key files:**
- `docs/doctor_phase4_spec.md` — Full spec (306 lines)
- `docs/doctor_boundary_policy.md` — Policy rules (220 lines)

---

## External Stress Layer (OBSERVATIONS)

**Stage 4 Results** (`external_stress_layer/STAGE4_RESULTS.md`):
- ESL accuracy: 63.64%
- Partial F1: 74%
- Undefined recall: 39%

**Critical Finding**: Generator data quality issue — ground truth labels don't match signal content in some cases. Baseline accuracy of 25% is artificially low due to this, not Doctor quality.

---

## Era 5: Direction 2 — Dynamic Extraction (THIS SESSION)

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

| Component | Commit | Lines | Status |
|-----------|--------|-------|--------|
| Extraction schema spec | 3983580 | — | ✅ |
| `doctor/dynamic/extractor.py` | abbafa6→e56ecdc | 378 | ✅ |
| Checker protocol spec | — | — | ✅ |
| `doctor/dynamic/checker_generator.py` | 33cc073 | 1009 | ✅ |
| Spec alignment | 71f8d59 | — | ✅ |

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

## Registry Status

- **40 problems** in `doctor/registry/problem_registry.json`
- Core matchers: class_modifiers, function_modifiers, return_type, parameter types
- Enriched with description, reference_solution, arrangement_validator

---

## Key Files Map

| Component | Path |
|-----------|------|
| Session State | `SESSION_STATE.md` |
| Phase A/B Report | `docs/production_report_phase_ab.md` |
| Phase 4 Spec | `docs/doctor_phase4_spec.md` |
| Boundary Policy | `docs/doctor_boundary_policy.md` |
| Stress Results | `external_stress_layer/STAGE4_RESULTS.md` |
| Extraction | `doctor/dynamic/extractor.py` |
| Checker Gen | `doctor/dynamic/checker_generator.py` |
| Schema Spec | `docs/direction2_extraction_schema.md` |
| Checker Protocol | `docs/direction2_checker_protocol.md` |
| Problem Registry | `doctor/registry/problem_registry.json` |

---

## CURRENT TASK

### Task 3: Test checker_generator end-to-end

**Checklist:**
- [ ] Run checker_generator on validated schema (e.g., 2225G output)
- [ ] Verify generated checker passes all 4 protocol tests
- [ ] Fix any failures in checker_generator
- [ ] Commit working version

### After Task 3

Full Direction 2 loop: Statement → Extractor → Schema → Checker Gen → Checker → Evaluation

Then: Use as new evaluator for Phase 2 Perturbation (adversarial generation)

---

## Session Start Checklist

1. Read this file (`SESSION_HANDOFF.md`)
2. Check `SESSION_STATE.md` for Era 3 details
3. Run command from `session_init.md` if needed
4. Continue current task