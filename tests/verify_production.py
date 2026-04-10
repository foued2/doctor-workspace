"""
Production Verification — Layer 0.5 Integration
=================================================
Runs the full mixed-batch evaluation with the LLMDoctor (which now includes
Layer 0.5 implicit undefined detection).

Reports:
  - Confusion matrix (GT × Predicted)
  - Undefined recall, precision, F1
  - Partial→undefined shift rate
  - What false negatives are classified as
  - False positive rate on non-undefined cases
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path
from collections import defaultdict

from doctor.llm_doctor import LLMDoctor
from doctor.doctor_grader import DoctorGrader
from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator
from dataset_generator.adaptive_generator import AdaptiveGenerator

print("=" * 80)
print("PRODUCTION VERIFICATION — Layer 0.5 Integration")
print("=" * 80)

doctor = LLMDoctor()
evaluator = EnhancedEvaluator()
grader = DoctorGrader()

# ===========================================================================
# PART A: Main evaluation on mixed batch
# ===========================================================================
print("\n[A] Running mixed batch evaluation...")

gen = AdaptiveGenerator(seed=42)
internal_batch = gen.generate_batch(n=30, memory_fraction=0.5)
cases = []
for pub in internal_batch["public_cases"]:
    priv = internal_batch["private_key"].get(pub["case_id"])
    if priv:
        cases.append(StressCase(
            case_id=pub["case_id"], prompt=pub["prompt"],
            stress_kind=StressKind.MIXED, ground_truth=priv["ground_truth"],
            metadata={"contradiction": priv.get("contradiction", False),
                       "corrupted_label": priv.get("corrupted", False)},
        ))

rw = RealWorldDataInjector(seed=42)
cd = CrossDomainStressor(seed=42)
hc = HumanCraftedAttacks(seed=42)
esl_cases = rw.generate_cases(15) + cd.generate_cases(15) + hc.generate_cases()
cases.extend(esl_cases)

print(f"  Total: {len(cases)} cases ({len(internal_batch['public_cases'])} internal + {len(esl_cases)} ESL)")

# Run predictions
predictions = []
errors = []
for case in cases:
    try:
        pred = doctor.predict(case.prompt)
        predictions.append(pred)
    except Exception as e:
        errors.append(case.case_id)
        predictions.append({"label": "undefined", "confidence": 0.5,
                            "decision_path": [f"error:{e}"]})

if errors:
    print(f"  ⚠ {len(errors)} prediction errors: {errors[:5]}")

metrics = evaluator.evaluate_batch(cases, predictions)
result = grader.grade(cases, predictions, metrics.distribution_shift)
result["flags"]["correct_by_luck"] = metrics.correct_by_luck_count
result["flags"]["shift_score"] = metrics.distribution_shift.get("shift_score", 0.0)

print(f"\n  Grade: {result['grade']:.4f} ({result['grade_letter']})")
print(f"  Rule_Score: {result['rule_score']:.4f}")
print(f"  Wrong@HighConf: {result['flags']['wrong_at_high_conf']*100:.1f}%")
print(f"  Shift Score: {result['flags']['shift_score']:.4f}")
print(f"  Correct F1: {result['breakdown']['correct_f1']*100:.1f}%")
print(f"  Partial F1: {result['breakdown'].get('partial_f1', 'N/A')}")
print(f"  Undefined Recall: {result['breakdown']['undefined_recall']*100:.1f}%")
print(f"  Undefined F1: {result['breakdown'].get('undefined_f1', 0)*100:.1f}%")

# ===========================================================================
# PART B: Confusion Matrix
# ===========================================================================
print("\n" + "=" * 80)
print("[B] CONFUSION MATRIX — Ground Truth × Predicted")
print("=" * 80)

labels = ["correct", "partial", "incorrect", "undefined"]
cm = defaultdict(lambda: defaultdict(int))

for case, pred in zip(cases, predictions):
    gt = case.ground_truth
    p = pred.get("label", "incorrect")
    cm[gt][p] += 1

# Header
header = f"{'GT \\ Pred':<14}"
for lbl in labels:
    header += f"{lbl:>12}"
header += f"{'Recall':>10}"
print(header)
print("-" * len(header))

for gt_lbl in labels:
    row = f"{gt_lbl:<14}"
    gt_total = sum(cm[gt_lbl].values())
    if gt_total == 0:
        row += f"{'(none)':>12}"
        for _ in labels[1:]:
            row += f"{'':>12}"
        row += f"{'N/A':>10}"
        print(row)
        continue

    for pred_lbl in labels:
        count = cm[gt_lbl][pred_lbl]
        row += f"{count:>12}"

    # Recall for this GT class
    tp = cm[gt_lbl][gt_lbl]
    recall = tp / gt_total if gt_total > 0 else 0.0
    row += f"{recall:>9.1%}"
    print(row)

print()

# Undefined-specific analysis
print("--- Undefined Analysis ---")
undef_gt_total = sum(cm["undefined"].values())
if undef_gt_total > 0:
    undef_recall = cm["undefined"]["undefined"] / undef_gt_total
    # What false negatives are classified as
    undef_fn = {lbl: cnt for lbl, cnt in cm["undefined"].items() if lbl != "undefined"}
    print(f"  Undefined ground truth cases: {undef_gt_total}")
    print(f"  Correctly classified as undefined: {cm['undefined']['undefined']}")
    print(f"  Undefined recall: {undef_recall:.1%}")
    if undef_fn:
        print(f"  False negatives (missed undefined cases):")
        for misclassified_lbl, cnt in sorted(undef_fn.items(), key=lambda x: -x[1]):
            print(f"    → {misclassified_lbl}: {cnt} ({cnt/undef_gt_total:.1%})")
    else:
        print(f"  False negatives: 0 (all undefined cases detected ✓)")
else:
    print("  No undefined ground truth cases in batch")

# Undefined precision: of all cases predicted undefined, how many are truly undefined?
undef_pred_total = sum(cm[gt]["undefined"] for gt in labels)
if undef_pred_total > 0:
    undef_precision = cm["undefined"]["undefined"] / undef_pred_total
    print(f"\n  Undefined precision: {undef_precision:.1%}")
    print(f"  Cases predicted 'undefined': {undef_pred_total}")
    # What non-undefined cases are falsely called undefined?
    undef_fp = {gt: cnt for gt in labels if gt != "undefined" for cnt_val in [cm[gt]["undefined"]] if cnt_val > 0 for cnt in [cnt_val]}
    if undef_fp:
        print(f"  False positives (non-undefined called 'undefined'):")
        for gt_lbl in labels:
            cnt = cm[gt_lbl]["undefined"]
            if cnt > 0 and gt_lbl != "undefined":
                print(f"    → GT={gt_lbl}: {cnt}")
else:
    print(f"\n  Undefined precision: N/A (no cases predicted 'undefined')")

# Partial→undefined shift rate
# Of all GT=undefined cases, what fraction landed as "partial"?
if undef_gt_total > 0:
    partial_fn = cm["undefined"]["partial"]
    shift_to_partial = partial_fn / undef_gt_total
    print(f"\n  Partial→undefined shift: {shift_to_partial:.1%} of undefined cases landed as 'partial'")
    print(f"  (Previous baseline: 100% — target is to see this drop)")

# ===========================================================================
# PART C: False Positive Analysis on Non-Undefined Cases
# ===========================================================================
print("\n" + "=" * 80)
print("[C] False Positive Analysis — Overclassification to 'undefined'")
print("=" * 80)

non_undef_labels = [lbl for lbl in labels if lbl != "undefined"]
false_undefined_cases = []

for case, pred in zip(cases, predictions):
    if case.ground_truth != "undefined" and pred.get("label") == "undefined":
        false_undefined_cases.append((case, pred))

if false_undefined_cases:
    print(f"  {len(false_undefined_cases)} non-undefined cases classified as 'undefined':\n")
    for case, pred in false_undefined_cases[:10]:
        print(f"  Case: {case.case_id} | GT={case.ground_truth}")
        print(f"    Conf={pred['confidence']} Kind={pred['confidence_kind']}")
        print(f"    Path={pred['decision_path']}")
        # Show first 120 chars of prompt
        prompt_preview = case.prompt[:120].replace("\n", " ")
        print(f"    Prompt: '{prompt_preview}...'")
        print()
    if len(false_undefined_cases) > 10:
        print(f"  ... and {len(false_undefined_cases) - 10} more")
else:
    print("  ✓ Zero non-undefined cases classified as 'undefined'")

# ===========================================================================
# PART D: Confidence Calibration for Undefined Predictions
# ===========================================================================
print("\n" + "=" * 80)
print("[D] Confidence Calibration — Undefined Predictions")
print("=" * 80)

undef_preds = []
for case, pred in zip(cases, predictions):
    if pred.get("label") == "undefined":
        undef_preds.append((case.ground_truth, pred["confidence"], pred.get("confidence_kind", "")))

if undef_preds:
    print(f"  Total 'undefined' predictions: {len(undef_preds)}")
    correct_undef = sum(1 for gt, _, _ in undef_preds if gt == "undefined")
    print(f"  Correct (GT=undefined): {correct_undef}")
    print(f"  Incorrect (GT≠undefined): {len(undef_preds) - correct_undef}")

    conf_correct = [c for gt, c, _ in undef_preds if gt == "undefined"]
    conf_incorrect = [c for gt, c, _ in undef_preds if gt != "undefined"]

    if conf_correct:
        print(f"  Confidence on correct undefined: min={min(conf_correct):.2f} max={max(conf_correct):.2f} mean={sum(conf_correct)/len(conf_correct):.2f}")
    if conf_incorrect:
        print(f"  Confidence on false-positive undefined: min={min(conf_incorrect):.2f} max={max(conf_incorrect):.2f} mean={sum(conf_incorrect)/len(conf_incorrect):.2f}")

    # Distribution of confidence kinds
    kinds = defaultdict(int)
    for _, _, kind in undef_preds:
        kinds[kind] += 1
    print(f"  Confidence kinds: {dict(kinds)}")
else:
    print("  No 'undefined' predictions made")

# ===========================================================================
# PART E: Target Check
# ===========================================================================
print("\n" + "=" * 80)
print("[E] TARGET CHECK")
print("=" * 80)

undef_recall = result['breakdown']['undefined_recall']
targets = [
    ("Undefined Recall > 70%", undef_recall > 0.70, f"{undef_recall*100:.1f}%"),
    ("Wrong@HighConf < 40%", result['flags']['wrong_at_high_conf'] < 0.40, f"{result['flags']['wrong_at_high_conf']*100:.1f}%"),
    ("Correct F1 > 60%", result['breakdown']['correct_f1'] > 0.60, f"{result['breakdown']['correct_f1']*100:.1f}%"),
    ("Shift Score < 0.4", result['flags']['shift_score'] < 0.4, f"{result['flags']['shift_score']:.4f}"),
]

all_met = True
for name, met, value in targets:
    status = "✓" if met else "✗"
    print(f"  {status} {name}: {value}")
    if not met:
        all_met = False

# Additional: partial→undefined shift
if undef_gt_total > 0:
    shift_rate = cm["undefined"]["partial"] / undef_gt_total
    print(f"  {'✓' if shift_rate < 0.5 else '✗'} Partial-as-undef rate < 50%: {shift_rate:.1%}")

print(f"\n{'='*80}")
if all_met:
    print("✓ ALL PRIMARY TARGETS MET")
else:
    print("⚠ Some targets not met — see values above")
print(f"{'='*80}")

# ===========================================================================
# Save confusion matrix to file for reference
# ===========================================================================
output = {
    "confusion_matrix": {gt: dict(preds) for gt, preds in cm.items()},
    "undefined_recall": undef_recall,
    "undefined_precision": cm["undefined"]["undefined"] / undef_pred_total if undef_pred_total > 0 else 0.0,
    "undefined_fp_cases": [(c.case_id, c.ground_truth, p["confidence"], p["decision_path"])
                            for c, p in false_undefined_cases],
    "total_cases": len(cases),
    "errors": errors,
}

out_path = Path(__file__).parent.parent / "layer05_results.json"
with open(out_path, "w") as f:
    json.dump(output, f, indent=2, default=str)
print(f"\n  Results saved to {out_path}")
