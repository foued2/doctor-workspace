# Project Cleanup Analysis

## Summary

This document identifies potentially unnecessary files and folders in the project.

---

## EMPTY / DEAD DIRECTORIES

### `adversarial_memory/`
**Status:** Empty (0 files)
**Action:** DELETE

---

## LIKELY UNNECESSARY

### `Learning/`
**Files:** 3 (Notes, memory.json, Topics)
**Assessment:** Appears to be old learning notes, not part of doctor project
**Action:** REVIEW - likely delete

### `other/`
**Files:** 15 LeetCode solutions from other projects
**Assessment:** LeetCode solutions unrelated to doctor project
**Action:** DELETE

### `solutions/`
**Files:** 1,453 LeetCode solutions
**Assessment:** Massive collection of LeetCode solutions, clearly not part of doctor core
**Action:** DELETE (move to separate repo if needed)

### `reports/`
**Files:** 19 files (timestamped JSON reports, copilot audit)
**Assessment:** One-off experiment reports, not part of current workflow
**Action:** DELETE (results already captured in scratch artifacts)

### `fuzz_reports/`
**Files:** 30 log/txt files from fuzzing experiments
**Assessment:** One-off fuzzing results
**Action:** DELETE

---

## ROOT LEVEL ONE-OFF FILES

| File | Assessment |
|------|------------|
| `123.py` | Unnamed, likely experimental |
| `_git_diff.txt` | Git artifact, regenerate as needed |
| `_git_log.txt` | Git artifact, regenerate as needed |
| `_predict_output.txt` | One-off prediction output |
| `predict_method.txt` | One-off notes |
| `apply_fix2.py` | Old fix, superseded |
| `apply_fix2b.py` | Old fix, superseded |
| `audit_*.py` (6 files) | Old audits, results in scratch |
| `syntax_check_results.txt` | One-off |
| `sanity_report.txt` | One-off |
| `leetcode_results.txt` | One-off results |
| `workspace_log.md` | Redundant with session_state files |
| `code_only_baseline.json` | One-off |
| `layer05_results.json` | One-off |
| `production_log.jsonl` | REVIEW - may be needed |
| `QWEN_SHARED_BRIEFING.md` | REVIEW - may be shared context |

---

## SCRATCH DIRECTORY

**Files:** ~90 files

### Keep (active artifacts):
- `trace_first_artifact_*.json` - Frozen experiment artifacts
- `phase1_status.json` - Machine-readable status
- `delta_experiment.py` - Framework

### Keep (useful reports):
- `PHASE1_CLOSURE_CHECKLIST.md` - Current guidance
- `SESSION_REPORT_20260414.md` - Session record
- `system_integrity_report.json` - System validation
- `DELTA_CORRECTION.md` - Philosophical correction

### DELETE (one-off experiments):
- `*_v2.py`, `*_v3.py`, `*_v4.py` - Superseded versions
- `*_final.py`, `*_final_*.py` - Superseded versions
- `*_probe*.py` (5 files) - Superseded
- `three_probe_*.py` (5 files) - Superseded
- `wrong_high_*.py` (4 files) - Debug artifacts
- `show_incorrect.py` - Debug artifact
- `test_partial_solutions.py` - Debug artifact
- `test_severity.py` - Debug artifact
- `read_lines*.py` (3 files) - Debug artifacts
- `extract.py` - Debug artifact
- `read_rules.py` - Debug artifact
- `cleanup_tasks*.py` - One-off
- `finalize_llm_doctor.py` - One-off
- `git_llm_doctor.py` - One-off
- `clean_llm_doctor.py` - One-off
- `mypy_report*.txt` - One-off lint reports
- `pytest_report.txt` - One-off
- `ruff_report.txt` - One-off
- `lines_extract.txt` - Debug artifact
- `evidence_policy*.txt` - Debug artifacts
- `evidence_comparison*.txt` - Debug artifact
- `evidence_has_error_test.txt` - Debug artifact
- `trace_layer_raw_output.txt` - Debug artifact
- `b_schema_hospital_elevator.json` - Debug artifact

### Keep (still used):
- `run_trace_first.py` - Entry point
- `run_offline_analysis.py` - Entry point
- `stress_test_trust.py` - Validation
- `adversarial_coverage.py` - Framework
- `structural_partition.py` - Framework
- `regime_stability.py` - Framework
- `calibrate_s_ref.py` - Framework
- `run_confidence_correlation.py` - Framework
- `check_timing_stability.py` - Framework
- `validate_ingestion_e2e.py` - Framework
- `trace_failure_root_cause.py` - Framework
- `debug_critical_failures.py` - Framework
- `evidence_policy.py` - Framework

---

## DUPLICATE / SUPERSEDED

### Root vs scratch audit files:
| Root | Scratch | Action |
|------|---------|--------|
| `audit_nqueens_all.py` | `audit_nqueens.py` | DELETE root |
| `audit_all_merge.py` | (none) | DELETE |
| `audit_merge_*.py` (4 files) | (none) | DELETE |
| `audit_nqueens_partial.py` | (none) | DELETE |

---

## VERSION CONTROL ARTIFACTS

### Duplicate pycache directories:
- Multiple Python version cache files (312, 313, 314)
**Action:** Add to `.gitignore` and delete

### `.venv1/`
Duplicate of `.venv/`
**Action:** DELETE

---

## RECOMMENDED ACTIONS

### Immediate (safe deletes):
1. `adversarial_memory/` - DELETE
2. `fuzz_reports/` - DELETE
3. `reports/` - DELETE
4. `other/` - DELETE
5. `solutions/` - DELETE (or move to separate repo)
6. `123.py` - DELETE
7. `apply_fix2.py`, `apply_fix2b.py` - DELETE
8. `_git_*.txt`, `_predict_*.txt`, `predict_method.txt` - DELETE
9. `syntax_check_results.txt`, `sanity_report.txt` - DELETE
10. Root `audit_*.py` files (6) - DELETE
11. `.venv1/` - DELETE

### Review before delete:
1. `workspace_log.md` - REVIEW (may have history)
2. `QWEN_SHARED_BRIEFING.md` - REVIEW (shared context)
3. `production_log.jsonl` - REVIEW (may be needed)
4. `Learning/` - DELETE (3 files)
5. `leetcode_results.txt` - DELETE

### Scrub scratch directory:
Delete ~50 one-off experiment files

### Add to .gitignore:
- `**/__pycache__/`
- `**/*.pyc`
- `.venv1/`

---

## ESTIMATED SPACE SAVINGS

| Item | Files | 
|------|-------|
| `solutions/` | ~1,453 |
| `reports/` | ~19 |
| `fuzz_reports/` | ~30 |
| Root one-offs | ~20 |
| Scratch one-offs | ~50 |
| **Total** | **~1,572** |

---

## CLEANUP PRIORITY

1. **HIGH** - Empty/dead directories (`adversarial_memory`)
2. **HIGH** - Unrelated code (`other/`, `solutions/`)
3. **HIGH** - One-off artifacts (`reports/`, `fuzz_reports/`, root one-offs)
4. **MEDIUM** - Duplicate audits
5. **LOW** - Scratch scrub (many small files)
6. **LOW** - Version artifacts (`.venv1`, pycache)
