# Project Progress

## System Status

### PROJECT A: LeetCode Learning System
- Suggestor: ✅ Multi-feature ranking integrated (skill-based, with topic detection + weak area boost)
- Doctor gates: ✅ Working (degraded mode, gate blocking, mode/validity tracking)
- End-to-end loop: ✅ Verified with simulated skill state
- Root cleanup: ✅ 25 files reorganized, 15 deleted, root is clean
- Duplicates: ✅ Verified none exist (41 unique top-level functions, 0 duplicates)
- **BLOCKER: API key needed for real AI evaluation** (DASHSCOPE / ANTHROPIC / OPENAI)

### PROJECT B: Adversarial Policy Evaluator (SEPARATE — do not mix with Project A)
- Dataset generator: ✅ Static generator exists (`generator.py`)
- Strict evaluator: ✅ Exists (`evaluator/strict_evaluator.py`) — batch metrics scorer
- **Adaptive generator: ✅ IMPLEMENTED** (Stage 2 — memory-driven adversary)
  - `failure_capture.py`: Error taxonomy (7 types), persistent failure logging (JSONL), pattern extraction, novelty check, adaptive weight computation
  - `adaptive_generator.py`: Weighted sampling, pattern mutation (3 escalation levels), cross-trap composition, memory-driven generation with novelty injection
  - Full loop proven: Generate → Fail → Capture → Learn → Adapt → Regenerate
  - Live demo: 7 failures in Round 1 → 5 failures in Round 2 (29% improvement)
  - 7 patterns extracted → 11 patterns after adaptation
  - Stratum weights shifted: A/B/C from 0.20→0.27 (fail zones boosted), D/E from 0.20→0.09 (mastered zones reduced)
- BLOCKER: Arbitration layer redesign (needs Doctor-like evaluator to consume generated cases)

## Project File Map
```
Project A (LeetCode):
  leetcode-tools/leetcode_doctor.py       — Doctor (code reviewer)
  leetcode-tools/leetcode_suggestor.py    — Suggestor (problem recommendations)
  leetcode-tools/doctor_interface.py      — Adapter layer
  leetcode-tools/execution_controller.py  — Execution + I/O controller
  leetcode-tools/io_manager.py            — Atomic file operations
  leetcode-tools/utils.py                 — Shared chunk_items utility
  leetcode-tools/fuzz_suggestor.py        — Suggestor fuzzing suite
  leetcode-tools/stress_test_scorer.py    — Scorer stress tests
  doctor/raw_prompt_doctor.py             — RawPromptDoctor engine
  tests/                                  — All test scripts (16 files)

Project B (Adversarial Evaluator):
  dataset_generator/generator.py          — Adversarial policy case generator
  evaluator/strict_evaluator.py           — Batch evaluation metrics
  fuzz_reports/                           — Fuzzing reports + outputs
  reports/                                — Benchmark JSON results
```

## Known Issues
- ~~Doctor has duplicate functions~~ → **RESOLVED**: No actual duplicates found. The 34.9% "duplication ratio" comes from legitimate repeated patterns — 4 AI provider methods (`_call_openai`, `_call_ollama`, `_call_claude`, `_call_qwen`) each have their own error handler with the same fallback pattern. No copy-paste accidents or duplicate function definitions exist.
- Real API key not configured (DASHSCOPE_API_KEY missing)
- Skill state only tested with injected data

## Next Session Start
1. Read `session_init.md` and `progress.md` before doing anything
2. ~~Fix duplicate functions in `leetcode_doctor.py`~~ → **DONE**: Verified no duplicates exist
3. Configure API key and run real end-to-end test
4. Then move to evaluator improvements
5. **Import note**: `execution_controller.py` and `io_manager.py` moved to `leetcode-tools/` — all imports still work via sys.path setup

## Root File Reorganization (2026-04-08 Session 2)
All scattered root files categorized and moved:

**Moved to `leetcode-tools/` (4):**
- `execution_controller.py` — core system module
- `io_manager.py` — core I/O module
- `main.py` — entry point
- `DEGRADED_MODE_STATUS.md` — implementation status doc

**Moved to `tests/` (13):**
- `benchmark_runner.py`, `doctor_attack_benchmark.py`, `doctor_attack_benchmark_strict.py`
- `doctor_runtime.py`, `final_falsification_test.py`, `gate_validation_suite.py`
- `test_doctor_grading.py`, `test_doctor_hardening.py`, `three_way_perturbation.py`
- `validate_doctor.py`, `run_stress_tests.ps1`, `Run-Project.ps1`

**Moved to `fuzz_reports/` (1):**
- `.fuzz_ratings.txt`

**Moved to `.qwen/` (1):**
- `QWEN.md`

**Moved to `Learning/` (3):**
- `Notes` — Python tips & tricks
- `Topics` — competitive programming topic list
- `memory.json` — mistake pattern tracking

**Deleted (15 total across both sessions):**
- 9 one-time scripts (apply_*, diagnose_*, fix_phase4*, etc.)
- 4 unrelated learning files (Binary Search, Binary Tree, Fluent Python, the happy sam)
- 1 session summary (SESSION_RESUME_SUMMARY.md)
- 1 empty directory chain (path/)

## Files Modified This Session (2026-04-08)
- `leetcode_suggestor.py` — Multi-feature ranking integration:
  - Imported `load_skill_state`, `rank_problems`, `score_problem`, `SKILL_CATEGORIES`, `_detect_topic_with_threshold` from `leetcode_doctor`
  - Added `rank_problems_with_skill_state()` function with scoring breakdown
  - Added `_enrich_problem_with_topic()` to detect topic from problem title
  - Updated `suggest_problem()` to display skill state, weak areas, and scoring explanation
  - Falls back to rating-based ranking when no skill history exists
- `doctor_skill_state.json` — Created (injected for testing; real updates come from Doctor)
- `session_init.md` — Created (session bootstrap)
- `progress.md` — Created (this file)
