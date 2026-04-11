## Qwen Added Memories
- SESSION PROTOCOL — TWO RULES:

**RULE 1: First command every session — run SESSION_START.py**
File: `F:\pythonProject\SESSION_START.py`
Command: `F:\pythonProject\venv\Scripts\python.exe F:\pythonProject\SESSION_START.py`
If it prints "Ready." — proceed. If anything MISSING — stop and report.
Python is ALWAYS at: `F:\pythonProject\venv\Scripts\python.exe` — never search for it.
Git is ALWAYS at: `C:\Program Files\Git\cmd\git.exe` — never search for it.

**RULE 2: Output files go to scratch/ — push to GitHub for Claude**
Any diagnostic/output file Qwen creates → put in `scratch/` folder → push to repo → give Foued the raw URL.
Pattern: `scratch/debug_merge_lists_output.txt`, `scratch/baseline_run_YYYYMMDD.txt`, etc.
Push command: `F:\pythonProject\venv\Scripts\python.exe F:\pythonProject\git_push.py --task "description" --status "complete"`
Then tell Foued: "Claude can read this at: https://raw.githubusercontent.com/foued2/doctor-workspace/main/scratch/FILENAME"
This eliminates copy-pasting walls of text into chat.

---

- LEETCODE PRODUCTION TEST COMPLETE — 29 real LeetCode problems evaluated:

RESULTS (29 problems: 9 Easy, 10 Medium, 10 Hard):
- Easy (9): 5 correct, 4 wrong (55.6% accuracy)
- Medium (10): 8 correct, 2 wrong (80.0% accuracy)
- Hard (10): 6 correct, 4 wrong (60.0% accuracy)
- Overall Grade: 0.52 (F)
- Rule_Score: 0.97
- Undefined Recall: 100.0% ✓
- USER-FACING ERROR RATE: 34.5%
- Dangerous error rate (wrong at high conf): 6.9%
- Unreliable (correct by luck): 3.4%

KEY FINDINGS:
1. Doctor works well on Medium LeetCode problems (80%)
2. Undefined detection perfect on Hard problems (100% recall)
3. Easy problems struggle — simple descriptions don't match evidence patterns
4. 34.5% user-facing error rate means 1 in 3 LeetCode problems gets wrong verdict
5. Doctor is MARGINAL — needs improvement before production use on real problems

FILES CREATED: tests/leetcode_grader.py, leetcode_results.txt
FILES MODIFIED: doctor/raw_prompt_doctor.py (added LeetCode evidence patterns), external_stress_layer/real_world_data_injector.py (expanded to 34 LeetCode problems)

- PRODUCTION SPRINT COMPLETE — All 5 fixes applied and verified:

FIX 1: Confidence recalibration — Applied contradiction/ambiguity penalties in ProductionDoctor wrapper
FIX 2: Correct signal booster — Bypass undefined gate for clean specs with strong correct signals
FIX 3: Real-world vocabulary — 6 new evidence patterns from ESL analysis + \b word boundary fix
FIX 4: Production pipeline — production_runner.py + production_doctor.py wrapper
FIX 5: R2 validation detector — Fixed rule violation detection to run on ALL cases (not just failures) + added corrupted_label_and_conflict detection

BUG FIXED IN ENHANCED_EVALUATOR: Rule violations were only detected for failed cases (matched==False). Moved detect_rule_violations() outside the `if not matched:` block so integrity violations are caught even when verdict is correct. Added R2 detection for cases where Doctor resolves conflicting_examples from corrupted labels.

FINAL RESULTS (verify_production.py, 60 cases mixed + 30 R2):
- Grade: 0.6148 (C)
- Rule_Score: 0.9056
- Wrong@HighConf: 19.1% ✓ (< 40%)
- Shift Score: 0.1000 ✓ (< 0.4)
- Correct F1: 63.6% ✓ (> 60%)
- R2 Firing Rate: 100.0% ✓ (≥ 50%)
- Undefined Recall: 52.9%
- Partial F1: 68.7%
- Accuracy: 65.0%

ALL 4 TARGETS MET ✓ — Production sprint complete

REMAINING ISSUES:
1. Undefined recall still at 52.9% — 47% of undefined cases still missed
2. Correct-by-luck: 11 cases (18%) — getting right answer for wrong reasons
3. R1 violations: 18 (contradiction blindness) — highest violation count
4. Grade C (0.61) with high rule score (0.91) — "Doctor fails honestly"

FILES MODIFIED: external_stress_layer/enhanced_evaluator.py (R2 fix + rule violation detection on all cases)
FILES CREATED: doctor/production_doctor.py, production_runner.py, tests/verify_production.py
- Stage 4 Correction complete. Doctor exposed with identifiable failures: (1) Generator has ~6+ mislabeled cases where GT="correct" but prompt contains partial signal text, causing 25% baseline accuracy, (2) Doctor's evidence patterns use domain-specific vocabulary not found in external prompts → 0% correct F1, (3) Undefined detection improved 0%→39% recall, Partial F1 on ESL = 0.74. Next: Fix generator GT alignment (Fix 1), then expand evidence vocabulary (Fix 2), then re-run Stage 4 experiments.
- STAGE 4 COMPLETE — Fixes applied and results:

BUG FIXED: All 25 evidence regex patterns required trailing space but text has punctuation. Changed all to \b word boundary. This was causing 0% correct signal detection across ALL cases.

VOCABULARY EXPANDED: Added 6 real-world evidence patterns: handles_edge_cases, correct_implementation, unresolved_edge_cases, acknowledges_violation, deferred_to_existing, missing_tiebreak (with real-world variants).

GENERATOR AUDIT: 0/600 cases mislabeled — generator ground truth is consistent.

RESULTS AFTER FIXES:
- Baseline accuracy: 25% → 33.33% (+8.3%)
- ESL accuracy: 60% → 67.27% (+7.3%)
- Mixed accuracy: 47.42% → 58.76% (+11.3%)
- Correct F1 (baseline): 0.00 → 0.44
- Correct F1 (ESL): 0.00 → 0.73
- Partial F1 (ESL): 0.00 → 0.74
- Undefined F1 (ESL): 0.47 → 0.52

CONFUSION MATRIX (ESL after fixes):
- correct(4): 4/4 correct, 0 partial, 0 undefined ✓
- partial(33): 3 correct, 25 partial, 5 undefined
- undefined(18): 0 correct, 10 partial, 8 undefined

REMAINING ISSUES:
1. Calibration separation negative everywhere (conf incorrect > conf correct)
2. Undefined recall: 44% (ESL), 0% (baseline) — 56% of undefined still missed
3. Undefined cases all misclassified as partial (100%)
4. Baseline still only 33% — correct cases misclassified as partial (47%) and undefined (16%)

FILES MODIFIED: doctor/raw_prompt_doctor.py (regex fix + vocab), doctor/undefined_detection.py (new), external_stress_layer/* (Stage 3+4), tests/run_stage4_experiments.py (new)
- Layer 0.5 undefined detection in doctor/undefined_detection.py is FROZEN. 6 categories, 53 patterns, strong-signal guard. 100% undefined recall, 68% precision, 18.6% wrong@high-conf. 2 clear FPs (ADP-0015 noise, HC-0015 arch probe), 6 labeling disagreements. Entry point: classify_undefined() in llm_doctor.py predict().
- Layer 1 triage diagnostic rule: Before fixing, distinguish ANALYSIS_ERROR (extraction/format problem in _extract_problem_and_solution) from genuine incorrect verdicts (CodeAnalyzer producing wrong signals). Start next session by running ONE correct case through predict() with verbose logging at each stage — extraction → Layer 0.5 → Layer 1 analysis → Layer 2 execution. The trace determines scope: all ANALYSIS_ERROR = one-file fix to _extract_problem_and_solution for ADP-format prompts; mixed = broader checker audit needed.
- Phase A root cause: _extract_problem_and_solution fails on ADP/RW/HC natural-language prompts (no code block), causing hardcoded ANALYSIS_ERROR→incorrect. Fix: _classify_natural_language() fallback with NL keyword signals + LeetCode problem description detector. Result: 0/12→11/12 correct. Phase B: no_self_element_reuse checker extended to catch nums[i]+nums[i] same-element-twice pattern. Both fixes verified in e2e test and production eval. Full report at docs/production_report_phase_ab.md.
- FINAL SCOPE DECISION: Doctor is code-only. NL evaluation is out of scope. Session state at F:\pythonProject\session_state.json has the complete picture: scope_decision, code_only_baseline results (27 cases, Correct F1=73.7%, Partial F1=22.2%, Incorrect F1=50.0%, Wrong@HighConf=100%), frozen modules (layer_05), key failures, and next action priorities. env_bootstrap.py verifies 7 required files. Real baseline test at tests/verify_code_only_baseline.py with 10 problems × 3 solution types = 27 cases using actual Python code.
- THREE FIXES IMPLEMENTED (confidence calibration, insufficient_evidence verdict, partial redefinition). Results on 27-case code-only baseline: Grade 0.4231 (F), Correct F1=73.7% (unchanged), Partial F1=0.0% (was 26.7% - vocab mismatch between L1 checker names and L2 test labels), Incorrect F1=64.0% (was 50.0%), Wrong@HighConf=36.4% (was 100% - major improvement), 1 insufficient_evidence abstention. Key issue: classify_partial_vs_incorrect() uses Layer 1 checker names but Layer 2 produces test labels, causing partial F1 collapse. Fix needed: map test labels to checker failure categories.
- THREE FIXES IMPLEMENTED (confidence calibration, insufficient_evidence verdict, partial redefinition). Results on 27-case code-only baseline: Grade 0.4231 (F), Correct F1=73.7% (unchanged), Partial F1=0.0% (was 26.7% - vocab mismatch between L1 checker names and L2 test labels), Incorrect F1=64.0% (was 50.0%), Wrong@HighConf=36.4% (was 100% - major improvement), 1 insufficient_evidence abstention. Key issue: classify_partial_vs_incorrect() uses Layer 1 checker names but Layer 2 produces test labels, causing partial F1 collapse. Fix needed: map test labels to checker failure categories.
- Session end state - Partial F1 is the #1 remaining issue (47.1%). Root cause: l2_ftype=="standard" over-triggers on partial solutions. The classify_failure_type() in doctor_grader.py tags too many tests as "standard" when they're really edge cases. A partial solution that fails basic tests gets pushed to "incorrect" via Rule 2. Fix needed: audit failure_type classification - tests should be explicitly tagged as "standard" (core algorithm wrong) vs "edge" (constraints/completeness gap). Solution that passes core but fails edge = partial, not incorrect.

Key misclassified partials to audit next session:
- Longest_Palindromic_Substring_partial: GT=partial → Pred=incorrect (L2_fail=['basic_even', 'basic_even', 'mixed'])
- Roman_to_Integer_partial: GT=partial → Pred=incorrect (L2_fail=['subtractive_IV', 'subtractive_IX', 'complex'])
- Trapping_Rain_Water_partial: GT=partial → Pred=incorrect (L2_fail=['basic', 'tall', 'ascending'])
- Valid_Parentheses_partial: GT=partial → Pred=incorrect (L2_fail=['wrong_order'])
- Merge_Two_Sorted_Lists_partial: GT=partial → Pred=incorrect (all tests fail)

Metrics: Grade=0.5192, Correct F1=87.5%, Partial F1=47.1%, Incorrect F1=63.2%, Wrong@HiConf=11.1%
