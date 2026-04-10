# Layer 0.5 — Known False Positives (Frozen)

## Status: FROZEN
Layer 0.5 undefined detection is complete. No further tuning recommended.
- Undefined recall: 100.0% (target >70%)
- Undefined precision: 68.0%
- Wrong@HighConf: 18.6% (target <40%)
- Partial→undefined drift: 0.0% (was 100% — primary failure mode eliminated)

---

## 2 Clear False Positives (Detection Errors)

### ADP-0015 (GT=correct) — Noise Pattern
**Score:** 0.77, **Signals:** 2 (underspecified_edges + normative_opinion_ambiguity)  
**Prompt snippet:** "The description mixes relevant records with logs, habits, legacy notes, and operational quirks..."  
**Why it fires:** "mixes relevant records with logs, habits" triggers normative patterns (selection among alternatives) and "operational quirks" triggers underspecified_edges.  
**Root cause:** The adaptive generator injects noise text ("logs, habits, legacy notes") that accidentally matches undefined heuristics. The ground truth is correct — the scoring rules are well-defined, only the prompt text is noisy.  
**Fix option (deferred):** Could add a negation pattern or reduce normative category weight, but risk of regressing real normative cases (RW-0010/RW-0011) outweighs fixing 1 FP.

### HC-0015 (GT=partial) — Architecture Probe
**Score:** 0.78, **Signals:** 3 (unresolved_conflicts + multiple_interpretations + contradictory_constraints)  
**Prompt snippet:** "CASE: Doctor architecture test... No explicit undecidable target... however the specification contains..."  
**Why it fires:** This case is *designed* to probe the Doctor's edge cases — it deliberately includes signals from multiple undefined categories to test whether the Doctor overtriggers. It has real contradictory language and competing objectives.  
**Root cause:** The test case is a stress test that happens to be labeled "partial" but reads as genuinely underspecified. Layer 0.5 is arguably correct here.  
**Fix option (deferred):** None practical. This is a borderline case by design.

---

## 6 Labeling Disagreements (Not Detection Errors)

These cases have genuine specification gaps but GT="partial" because a partial solution exists:

| Case | GT | Signals | Why Layer 0.5 fires | Why GT≠undefined |
|------|----|---------|---------------------|------------------|
| RW-0008 | partial | 2 | "Inconsistent behavior" in GitHub issue — genuine ambiguity | Partial solution exists (workaround) |
| RW-0007 | partial | 2 | "merge strategy" conflict in VSCode settings | Partial solution exists (pick one approach) |
| CD-0013 | partial | 1 | Grade Appeal: "to be determined" strong signal | Partial: appeal process is defined, timeline TBD |
| CD-0008 | partial | 1 | Rate Limiting: "No specification for burst handling" | Partial: basic rate limiting works, burst gap |
| HC-0010 | partial | 1 | "No definition of priority" — genuinely underspecified | Partial: arrival order processing works |
| HC-0005 | partial | 2 | Deceptive policy with conflicting signals | Partial: surface-level analysis possible |

These are **not** bugs in Layer 0.5 — the specs *are* underspecified. The labels call them "partial" because you can do *something* with them, not because they lack ambiguity.

---

## Confidence Calibration Limitation

- Correct undefined: mean confidence 0.88 (range 0.83–0.94)
- FP undefined: mean confidence 0.86 (range 0.85–0.88)
- **These are indistinguishable.** The short-circuit design fires before Layer 1/2 generates calibrating evidence.

Acceptable for now — the override is doing its job. Future work: add Layer 1/2 post-hoc calibration for undefined predictions if the grader uses confidence weighting.

---

## Next Target: Layer 1 Static Analysis Failure

**Correct F1 = 0.0%** — All 12 correct cases classified as "incorrect" via ANALYSIS_ERROR.
This is the dominant structural failure, predating Layer 0.5. See session_state.json for details.
