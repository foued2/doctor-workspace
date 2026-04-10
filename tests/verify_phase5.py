"""
Phase 5 Verification Script
=============================
Run a mixed batch (50/50 internal/ESL, 60 cases total).
Report:
- Calibration breakdown per verdict class
- Any correct_by_luck cases found
- Distribution shift score
- Whether shift score triggers novelty injection
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from pathlib import Path
from collections import defaultdict
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from doctor.raw_prompt_doctor import RawPromptDoctor
from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
from external_stress_layer.enhanced_evaluator import (
    EnhancedEvaluator,
    second_pass_eval,
    compute_calibration,
    compute_distribution_shift,
)
from dataset_generator.adaptive_generator import AdaptiveGenerator

print("=" * 80)
print("PHASE 5 VERIFICATION — Evaluation Pipeline Upgrade")
print("=" * 80)

# Initialize
doctor = RawPromptDoctor()
evaluator = EnhancedEvaluator()

# ── Step 1: Generate mixed batch (50/50 internal/ESL, 60 total) ─────────────
print("\n[1/5] Generating mixed batch (30 internal + 30 ESL)...")

# Internal cases
gen = AdaptiveGenerator(seed=42)
internal_batch = gen.generate_batch(n=30, memory_fraction=0.5)
internal_cases = []
case_id_counter = 1
for pub in internal_batch["public_cases"]:
    priv = internal_batch["private_key"][pub["case_id"]]
    internal_cases.append(StressCase(
        case_id=pub["case_id"],
        prompt=pub["prompt"],
        stress_kind=StressKind.MIXED,
        ground_truth=priv["ground_truth"],
        metadata={
            "source": "internal_generator",
            "stratum": priv["stratum"],
            "contradiction": priv.get("contradiction", False),
            "corrupted_label": priv.get("corrupted_label", False),
        },
    ))

# ESL cases
rw = RealWorldDataInjector(seed=42)
cd = CrossDomainStressor(seed=42)
hc = HumanCraftedAttacks(seed=42)
esl_cases = rw.generate_cases(15) + cd.generate_cases(15) + hc.generate_cases()

print(f"  Internal cases: {len(internal_cases)}")
print(f"  ESL cases: {len(esl_cases)}")

all_cases = internal_cases + esl_cases
print(f"  Total: {len(all_cases)}")

# ── Step 2: Run Doctor predictions ──────────────────────────────────────────
print("\n[2/5] Running Doctor predictions...")
predictions = []
for i, case in enumerate(all_cases):
    try:
        pred = doctor.predict(case.prompt)
        predictions.append(pred)
    except Exception as e:
        predictions.append({
            "case_id": case.case_id,
            "label": "undefined",
            "confidence": 0.5,
            "decision_path": ["error"],
        })
    if (i + 1) % 20 == 0:
        print(f"  Processed {i + 1}/{len(all_cases)} cases...", end='\r')
print(f"\n  ✓ Completed")

# ── Step 3: Run full evaluation with Phase 5 metrics ────────────────────────
print("\n[3/5] Running enhanced evaluation...")
metrics = evaluator.evaluate_batch(all_cases, predictions)

print(f"\n  Overall accuracy: {metrics.accuracy:.2%}")
print(f"  Failed cases: {metrics.failed_cases}")

# ── Step 4: Report Phase 5 metrics ──────────────────────────────────────────
print("\n[4/5] Phase 5 Metrics")

# Calibration
print("\n" + "=" * 80)
print("CALIBRATION BREAKDOWN")
print("=" * 80)

cal = metrics.calibration
print(f"\n  Correct verdicts, high confidence (>= 0.7): {cal['correct_verdicts_high_confidence']}")
print(f"  Correct verdicts, low confidence (< 0.7):   {cal['correct_verdicts_low_confidence']}")
print(f"  Wrong verdicts, high confidence (>= 0.7):   {cal['wrong_verdicts_high_confidence']} ← MOST DANGEROUS")
print(f"  Wrong verdicts, low confidence (< 0.7):     {cal['wrong_verdicts_low_confidence']}")
print(f"\n  Wrong-at-high-conf rate: {cal['wrong_high_confidence_pct']:.0%}")
if cal['flag_dangerous_overconfidence']:
    print(f"  ⚠ DANGEROUS OVERCONFIDENCE FLAGGED (>20% of wrong verdicts at high confidence)")
else:
    print(f"  ✓ Overconfidence within acceptable bounds")

# Per-verdict breakdown
print(f"\n  Per-verdict breakdown:")
for verdict, counts in cal.get('by_verdict', {}).items():
    total = sum(counts.values())
    print(f"    {verdict} ({total} total):")
    print(f"      Correct high conf: {counts['correct_high']}, Correct low conf: {counts['correct_low']}")
    print(f"      Wrong high conf: {counts['wrong_high']}, Wrong low conf: {counts['wrong_low']}")

# Second-pass evaluation
print("\n" + "=" * 80)
print("SECOND-PASS EVALUATION")
print("=" * 80)

failure_mode_counts = defaultdict(int)
for sp in metrics.second_pass_results:
    failure_mode_counts[sp["failure_mode"]] += 1

print(f"\n  Failure mode distribution:")
for mode, count in sorted(failure_mode_counts.items(), key=lambda x: -x[1]):
    pct = count / len(metrics.second_pass_results) * 100
    print(f"    {mode}: {count} ({pct:.0f}%)")

print(f"\n  Correct-by-luck cases: {metrics.correct_by_luck_count}")
print(f"  Wrong-with-violation cases: {metrics.wrong_with_violation_count}")

# Show correct_by_luck cases if any
correct_by_luck_cases = [
    (case, pred, sp) for case, pred, sp in zip(all_cases, predictions, metrics.second_pass_results)
    if sp["failure_mode"] == "correct_by_luck"
]

if correct_by_luck_cases:
    print(f"\n  Correct-by-luck case details (first 5):")
    for case, pred, sp in correct_by_luck_cases[:5]:
        print(f"    Case {case.case_id}:")
        print(f"      Ground truth: {case.ground_truth}, Doctor: {pred['label']} (conf: {pred['confidence']:.2f})")
        print(f"      Rule violations: {sp['rule_violations']}")
else:
    print(f"\n  No correct-by-luck cases found")

# Distribution shift
print("\n" + "=" * 80)
print("DISTRIBUTION SHIFT DETECTION")
print("=" * 80)

shift = metrics.distribution_shift
print(f"\n  ESL accuracy: {shift['esl_accuracy']:.2%} ({shift['esl_total']} cases)")
print(f"  Internal accuracy: {shift['internal_accuracy']:.2%} ({shift['internal_total']} cases)")
print(f"  Shift score: {shift['shift_score']:.4f}" if shift['shift_score'] is not None else "  Shift score: N/A (insufficient data)")

if shift['needs_novelty_injection']:
    print(f"  ⚠ NOVELTY INJECTION REQUIRED (shift_score > 0.4)")
    print(f"    → Next batch should pull 30% from ESL cases directly")
else:
    print(f"  ✓ Distribution within bounds (no novelty injection needed)")

# ── Step 5: Summary ─────────────────────────────────────────────────────────
print("\n[5/5] Phase 5 Verification Summary")

print("\n" + "=" * 80)
print("PHASE 5 VERIFICATION SUMMARY")
print("=" * 80)

# Overall assessment
issues = []
strengths = []

if cal['flag_dangerous_overconfidence']:
    issues.append("Dangerous overconfidence detected")
else:
    strengths.append("Calibration within acceptable bounds")

if metrics.correct_by_luck_count > 0:
    issues.append(f"{metrics.correct_by_luck_count} correct-by-luck cases found")
else:
    strengths.append("No correct-by-luck cases")

if shift['needs_novelty_injection']:
    issues.append(f"Distribution shift detected (score: {shift['shift_score']:.4f})")
else:
    strengths.append("Distribution stable")

print(f"\n  Strengths:")
for s in strengths:
    print(f"    ✓ {s}")

if issues:
    print(f"\n  Issues:")
    for i in issues:
        print(f"    ⚠ {i}")

print(f"\n{'='*80}")
print("✓ PHASE 5 VERIFICATION COMPLETE")
print(f"{'='*80}")
