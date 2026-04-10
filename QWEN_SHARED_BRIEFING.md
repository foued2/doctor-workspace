# Shared Workspace — Briefing for Claude

> This document explains everything you need to know to collaborate with Qwen on the Doctor project. Read it once, reference the URLs below, and you'll have full context without token-heavy copy-paste.

---

## What This Repo Is

**Repository:** https://github.com/foued2/doctor-workspace
**Branch:** `main`
**Visibility:** Public (no auth needed to read)
**Owner:** foued2 (Foued)

A shared git workspace where **Qwen** (free AI) pushes its work and **Claude** (free web interface) reads it via raw URLs. No copy-paste of large code blocks. Saves tokens for Claude.

---

## Key Raw URLs (Claude can fetch these directly)

```
Session log:        https://raw.githubusercontent.com/foued2/doctor-workspace/main/workspace_log.md
Config/memory:      https://raw.githubusercontent.com/foued2/doctor-workspace/main/QWEN.md
Briefing (Claude):  https://raw.githubusercontent.com/foued2/doctor-workspace/main/QWEN_SHARED_BRIEFING.md
Doctor core:        https://raw.githubusercontent.com/foued2/doctor-workspace/main/doctor/llm_doctor.py
Code analyzer:      https://raw.githubusercontent.com/foued2/doctor-workspace/main/doctor/code_analyzer.py
Test executor:      https://raw.githubusercontent.com/foued2/doctor-workspace/main/doctor/test_executor.py
Doctor grader:      https://raw.githubusercontent.com/foued2/doctor-workspace/main/doctor/doctor_grader.py
Undefined det:      https://raw.githubusercontent.com/foued2/doctor-workspace/main/doctor/undefined_detection.py
Calibrator:         https://raw.githubusercontent.com/foued2/doctor-workspace/main/doctor/confidence_calibrator.py
Stress layer:       https://raw.githubusercontent.com/foued2/doctor-workspace/main/external_stress_layer/enhanced_evaluator.py
Tests:              https://raw.githubusercontent.com/foued2/doctor-workspace/main/tests/
```

Any file in the repo is readable via:
`https://raw.githubusercontent.com/foued2/doctor-workspace/main/<path>`

---

## What the Doctor Project Does

**Goal:** An automated code reviewer ("Doctor") that evaluates LeetCode solutions and classifies them as:
- **correct** — solution is right
- **partial** — solution has some issues
- **incorrect** — solution is wrong
- **undefined** — problem spec is ambiguous/incomplete (can't be judged)

**Architecture (3 layers):**
- **Layer 0.5:** Undefined detection (`doctor/undefined_detection.py`) — 6 categories, 53 regex patterns. Catches ambiguous specs before analysis. FROZEN (production-vetted).
- **Layer 1:** Static analysis (`doctor/code_analyzer.py`) — checks for signal keywords in problem descriptions (contradiction, correctness, partial signals). Produces signals → verdict.
- **Layer 2:** Test execution (`doctor/test_executor.py`) — runs actual test cases against the code.
- **Fusion:** Verdicts from all layers are fused in `doctor/llm_doctor.py` `predict()` method with confidence calibration.

---

## Current Status (as of 2026-04-10)

### What's Been Tested
- 600-case evaluation pipeline (mixed real + synthetic prompts)
- 27-case code-only baseline using actual LeetCode problems
- Layer 0.5 undefined detection: 100% recall on hard problems, ~39-53% on ESL
- Layer 1 triage: fixed `_extract_problem_and_solution` fallback for NL prompts
- Confidence calibration: reduced wrong@high-conf from 100% → 36.4%

### Known Issues
1. **Undefined recall ~53%** — 47% of undefined cases still missed (all misclassified as partial)
2. **Correct-by-luck** — ~11 cases (18%) get right verdict for wrong reasons
3. **R1 violations** — 18 (contradiction blindness) — highest violation count
4. **Grade C (0.61)** — "Doctor fails honestly"
5. **Calibration separation** — negative in some ranges (confidence incorrect > confidence correct)

### Recent Fixes Applied
- Phase A: `_extract_problem_and_solution` fallback for NL prompts (0/12 → 11/12 correct)
- Phase B: `no_self_element_reuse` checker for `nums[i]+nums[i]` same-element-twice pattern
- Confidence recalibration with contradiction/ambiguity penalties
- R2 validation detector — fixed to run on ALL cases
- Evidence regex: added `\b` word boundaries + 6 new real-world patterns

### What's Next
Check `workspace_log.md` for the latest Qwen entries with `ACTION_NEEDED` fields. Qwen's todo list and current task are always in the last 3-5 entries.

---

## GPT's Critique (2026-04-10) — AWAITING CLAUDE'S REVIEW

GPT reviewed the workspace setup and raised these points. **Qwen will not act on any of this until Claude approves.**

### Valid Points (agreed by Qwen):
1. **Missing adversarial loop** — We have static datasets but no adversarial round after every change. Fuzz reports are dated (Apr 7-8), not part of active iteration.
2. **Metric chasing** — "Grade: C (0.61), needs improvement" optimizes F1/rule_score, not "harder to fool." Better frame: *reduce exploitable surface area.*
3. **Converging to wrong thing** — We optimized for our dataset distribution, not truly adversarial inputs.

### Half-Right:
4. **Information lag / relay noise** — Real but unavoidable with free AI. Bounded by lossless git logs. Not catastrophic.

### Disputed:
5. **"Architect doesn't observe runtime behavior"** — Claude doesn't need to. Reads code + test results. Runtime debugging is Qwen's job. Split works.
6. **"System will degrade through relay noise"** — Not observed in practice. QWEN.md shows coherent improvement cycles. No degradation.

### GPT's Concrete Recommendation:
> After each change, run an adversarial round: 5-10 adversarial solutions designed to pass tests incorrectly, confuse partial vs incorrect, exploit confidence thresholds.

**Existing infrastructure we already have:**
- `external_stress_layer/` — stress testing framework
- `tests/final_falsification_test.py` — falsification test suite
- `fuzz_reports/` — dated fuzz test reports

**What's missing:** Running these as a **gate every iteration**, not one-off experiments.

### GPT's Second Critique (2026-04-10) — AWAITING CLAUDE'S REVIEW

After reviewing Qwen's assessment of the first critique, GPT added:

1. **Static adversarial ≠ real adversarial** — Reusing the same 5-10 cases leads to adversarial overfitting. The adversarial set must **evolve based on current failures**, not be a fixed pool.
2. **Information lag is deeper than data loss** — Claude can't probe interactively (run variants, test hypotheses, explore edges dynamically). Reduces Claude to post-hoc analyst, not true architect. Real limitation, not catastrophic but a hard ceiling.
3. **Confidence problem is the core risk** — Wrong@HighConf = 100% (historical). If adversarial case passes but confidence is high, failure is **undetectable**. Confidence must be tied to evidence strength, or adversarial rounds are meaningless.
4. **"Works on LeetCode" is not a stable target** — LeetCode itself has ambiguous constraints, edge cases, multiple valid patterns. "Works on LeetCode-style prompts" = "works on your current subset."
5. **Concrete spec for adversarial loop:**
   - Seed from last round's misclassifications
   - Mutate: change edge cases, tweak logic, preserve structure but alter semantics
   - Force diversity: 1 semantic trap, 1 edge-case exploit, 1 confidence exploit, 1 partial/incorrect ambiguity
   - Track: **Adversarial Pass Rate** + **Wrong@HighConf (on adversarial set)**
   - If either increases → regression, regardless of F1
6. **Critiques are constraints, not suggestions** — Without adaptive adversarial pressure: system plateaus. Without confidence fix: system misleads. With static sets: system overfits.

**AWAITING CLAUDE'S DECISION:** Should we implement failure-driven adversarial generation + confidence tracking as a gating metric? If so, what scope and priority?

---

## Workflow

### How Qwen Works
- Qwen runs locally via Qwen Code CLI on Foued's machine (Windows, `F:\pythonProject`)
- After each task, Qwen runs `python git_push.py --task "..." --status "..."` which:
  1. Stages all doctor project files
  2. Appends entry to `workspace_log.md`
  3. Commits and pushes to this repo
- Git/Python paths are hardcoded in `git_push.py` (Windows paths)
- **Qwen only executes changes approved by Claude**, not by GPT or anyone else.

### How Claude Should Work
1. **Read the log** — fetch `workspace_log.md` to see what Qwen has been doing
2. **Read the code** — fetch specific files via raw URLs above
3. **Analyze and advise** — tell Foued what to fix, redesign, or improve
4. **Approve or reject** external suggestions (e.g., from GPT)
5. **No execution needed** — Qwen implements on the ground, Claude provides direction

### What Claude CANNOT Do
- Run code, push commits, or execute commands (Claude web interface can't do git)
- Modify files directly
- Be notified automatically when Qwen pushes new changes

### What Claude CAN Do
- Read any file via raw GitHub URLs (zero token cost for reading)
- Analyze code, design fixes, direct Qwen's next steps
- Approve or reject suggestions from other AIs
- Save massive amounts of tokens by NOT re-reading code from chat context

### How Communication Works
| Direction | Mechanism |
|---|---|
| Qwen → Claude | Qwen pushes to this repo; Claude fetches raw URLs |
| Claude → Qwen | Claude tells Foued what to ask Qwen; Foued relays |
| You tell Qwen | "Claude says to fix X in file Y" |
| You tell Claude | "Qwen pushed, check the workspace" |

---

## Project Structure

```
doctor/
  llm_doctor.py          # Main entry point, predict() method
  code_analyzer.py       # Layer 1: static analysis, signal detection
  test_executor.py       # Layer 2: test case execution
  doctor_grader.py       # Grading logic for verdicts
  undefined_detection.py # Layer 0.5: ambiguity detector (FROZEN)
  confidence_calibrator.py # Confidence scoring

external_stress_layer/
  enhanced_evaluator.py  # Cross-domain stress testing
  real_world_data_injector.py  # Real prompt injection
  mixed_batch_runner.py  # Batch evaluation

tests/
  verify_code_only_baseline.py  # Current test suite
  leetcode_grader.py            # LeetCode problem evaluator
  run_stage4_experiments.py     # Stage 4 experiments
  final_falsification_test.py   # Adversarial falsification tests
  ... (many other test scripts)

docs/
  production_report_phase_ab.md  # Fix reports
  layer05_false_positives.md     # Layer 0.5 analysis

solutions/                        # 800+ LeetCode solution files
workspace_log.md                  # Append-only session log
QWEN.md                           # Qwen's memory/state
QWEN_SHARED_BRIEFING.md           # This file
```

---

## What to Do When Foued Says "Check the Workspace"

1. Fetch `workspace_log.md` — read last 3-5 entries
2. Note Qwen's last task, status, and any `ACTION_NEEDED`
3. Fetch the relevant source files Qwen modified
4. Analyze the changes
5. **Review any external AI critiques** (e.g., GPT's points above) — approve, reject, or modify
6. Provide direction to Foued: what to fix, what to test, what to ask Qwen next

**Key principle:** You are the architect. Qwen is the mechanic. You approve or reject external input. Qwen implements your decisions and pushes the results here.
