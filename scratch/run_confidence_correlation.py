"""
Confidence Correlation Experiment — Median-Split Analysis
=========================================================

Tests the hypothesis: Doctor's confidence scores correlate with correctness.

Method:
  1. Run all 27 code-only baseline cases through predict()
  2. Collect (confidence, verdict_is_correct) for each case
  3. Split at median confidence → high_conf vs low_conf groups
  4. Compute P(verdict=correct | high_conf) vs P(verdict=correct | low_conf)
  5. Also compute P(error | high_conf) — the dangerous misclassification rate

The key signal the user flagged: partial cases confidently misclassified as correct.
That's the exact failure mode Doctor was built to catch — high confidence + wrong verdict.
The median split surfaces whether this pattern holds systematically across the 27 cases.
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from collections import defaultdict
from statistics import median

from doctor.llm_doctor import LLMDoctor, _extract_problem_and_solution
from external_stress_layer import StressCase, StressKind

# Import the 27 cases from the baseline
from tests.verify_code_only_baseline import SOLUTIONS


def main():
    print("=" * 80)
    print("CONFIDENCE CORRELATION EXPERIMENT — Median-Split Analysis")
    print("=" * 80)

    doctor = LLMDoctor()

    # ── Build cases (same as code-only baseline) ─────────────────────
    cases = []
    for key, sol in sorted(SOLUTIONS.items()):
        problem_name, sol_type = key.split("::")
        prompt = f"PROBLEM: {sol['problem']}\n\nSOLUTION:\n{sol['code']}"
        cases.append(StressCase(
            case_id=f"{problem_name.replace(' ', '_')}_{sol_type}",
            prompt=prompt,
            stress_kind=StressKind.MIXED,
            ground_truth=sol["ground_truth"],
        ))

    print(f"\nTotal cases: {len(cases)}")

    # ── Run predictions ──────────────────────────────────────────────
    print(f"Running predictions...")
    predictions = []
    for case in cases:
        pred = doctor.predict(case.prompt)
        predictions.append(pred)
        print(f"  {case.case_id:<40} pred={pred['label']:<12} conf={pred['confidence']:.2f}  ({pred.get('confidence_kind','?')})")

    # ── Collect confidence + correctness data ────────────────────────
    print(f"\n{'='*80}")
    print(f"DATA COLLECTION")
    print(f"{'='*80}")

    data = []
    for case, pred in zip(cases, predictions):
        conf = pred["confidence"]
        verdict_correct = (pred["label"] == "correct")
        gt_match = (pred["label"] == case.ground_truth)
        data.append({
            "case_id": case.case_id,
            "ground_truth": case.ground_truth,
            "predicted_label": pred["label"],
            "confidence": conf,
            "verdict_is_correct": verdict_correct,
            "matches_ground_truth": gt_match,
        })

    # Print per-case table
    print(f"\n{'Case':<40} {'GT':<12} {'Pred':<12} {'Conf':>6} {'VerdictCorrect':>15} {'MatchGT':>8}")
    print("-" * 95)
    for d in data:
        print(f"{d['case_id']:<40} {d['ground_truth']:<12} {d['predicted_label']:<12} {d['confidence']:>6.2f} {str(d['verdict_is_correct']):>15} {str(d['matches_ground_truth']):>8}")

    # ── Median Split ─────────────────────────────────────────────────
    confidences = [d["confidence"] for d in data]
    med = median(confidences)
    print(f"\n{'='*80}")
    print(f"MEDIAN SPLIT ANALYSIS")
    print(f"{'='*80}")
    print(f"  Median confidence: {med:.4f}")
    print(f"  Confidence range: [{min(confidences):.2f}, {max(confidences):.2f}]")
    print(f"  Confidence std (rough): {(max(confidences)-min(confidences))/4:.2f}")

    high_conf = [d for d in data if d["confidence"] >= med]
    low_conf = [d for d in data if d["confidence"] < med]

    print(f"\n  High confidence (≥ {med:.2f}): {len(high_conf)} cases")
    print(f"  Low confidence  (< {med:.2f}): {len(low_conf)} cases")

    # P(verdict=correct | high_conf)
    high_correct_verdicts = sum(1 for d in high_conf if d["verdict_is_correct"])
    p_correct_given_high = high_correct_verdicts / len(high_conf) if high_conf else 0.0

    # P(verdict=correct | low_conf)
    low_correct_verdicts = sum(1 for d in low_conf if d["verdict_is_correct"])
    p_correct_given_low = low_correct_verdicts / len(low_conf) if low_conf else 0.0

    # P(error | high_conf) — dangerous misclassification rate
    high_errors = sum(1 for d in high_conf if not d["matches_ground_truth"])
    p_error_given_high = high_errors / len(high_conf) if high_conf else 0.0

    # P(error | low_conf)
    low_errors = sum(1 for d in low_conf if not d["matches_ground_truth"])
    p_error_given_low = low_errors / len(low_conf) if low_conf else 0.0

    # Mean confidence for correct vs incorrect verdicts
    correct_verdict_confs = [d["confidence"] for d in data if d["verdict_is_correct"]]
    incorrect_verdict_confs = [d["confidence"] for d in data if not d["verdict_is_correct"]]
    mean_conf_correct = sum(correct_verdict_confs) / len(correct_verdict_confs) if correct_verdict_confs else 0.0
    mean_conf_incorrect = sum(incorrect_verdict_confs) / len(incorrect_verdict_confs) if incorrect_verdict_confs else 0.0

    # Mean confidence for GT-matching vs GT-mismatching
    gt_match_confs = [d["confidence"] for d in data if d["matches_ground_truth"]]
    gt_mismatch_confs = [d["confidence"] for d in data if not d["matches_ground_truth"]]
    mean_conf_gt_match = sum(gt_match_confs) / len(gt_match_confs) if gt_match_confs else 0.0
    mean_conf_gt_mismatch = sum(gt_mismatch_confs) / len(gt_mismatch_confs) if gt_mismatch_confs else 0.0

    print(f"\n  ── Conditional Probabilities ──")
    print(f"  P(verdict=correct | high_conf) = {p_correct_given_high:.1%}  ({high_correct_verdicts}/{len(high_conf)})")
    print(f"  P(verdict=correct | low_conf)  = {p_correct_given_low:.1%}  ({low_correct_verdicts}/{len(low_conf)})")
    print(f"  Delta (separation)             = {p_correct_given_high - p_correct_given_low:+.1%}")

    print(f"\n  ── Error Rates (mismatch with ground truth) ──")
    print(f"  P(error | high_conf) = {p_error_given_high:.1%}  ({high_errors}/{len(high_conf)})")
    print(f"  P(error | low_conf)  = {p_error_given_low:.1%}  ({low_errors}/{len(low_conf)})")

    print(f"\n  ── Mean Confidence by Outcome ──")
    print(f"  Mean conf when verdict=correct:   {mean_conf_correct:.3f}  (n={len(correct_verdict_confs)})")
    print(f"  Mean conf when verdict≠correct:   {mean_conf_incorrect:.3f}  (n={len(incorrect_verdict_confs)})")
    print(f"  Delta                               = {mean_conf_correct - mean_conf_incorrect:+.3f}")

    print(f"\n  Mean conf when matches GT:        {mean_conf_gt_match:.3f}  (n={len(gt_match_confs)})")
    print(f"  Mean conf when mismatches GT:     {mean_conf_gt_mismatch:.3f}  (n={len(gt_mismatch_confs)})")
    print(f"  Delta                               = {mean_conf_gt_match - mean_conf_gt_mismatch:+.3f}")

    # ── High-confidence misclassifications (the signal) ──────────────
    print(f"\n{'='*80}")
    print(f"HIGH-CONFIDENCE MISCLASSIFICATIONS (conf ≥ {med:.2f} AND wrong verdict)")
    print(f"{'='*80}")

    high_conf_errors = [d for d in high_conf if not d["matches_ground_truth"]]
    if high_conf_errors:
        for d in high_conf_errors:
            print(f"  ✗ {d['case_id']:<40} GT={d['ground_truth']:<12} Pred={d['predicted_label']:<12} Conf={d['confidence']:.2f}")
    else:
        print(f"  None — all high-confidence predictions match ground truth")

    # ── Partial cases specifically ───────────────────────────────────
    print(f"\n{'='*80}")
    print(f"PARTIAL CASES — Where do they land?")
    print(f"{'='*80}")

    partial_cases = [d for d in data if d["ground_truth"] == "partial"]
    for d in partial_cases:
        flag = ""
        if d["predicted_label"] == "correct":
            flag = " ⚠ MISCLASSIFIED AS CORRECT"
        elif d["predicted_label"] == "incorrect":
            flag = " → incorrectly (may be legitimate)"
        elif d["predicted_label"] == "partial":
            flag = " ✓ correct"
        print(f"  {d['case_id']:<40} Pred={d['predicted_label']:<12} Conf={d['confidence']:.2f}{flag}")

    partial_correct_preds = sum(1 for d in partial_cases if d["predicted_label"] == "correct")
    partial_correct_preds_high_conf = sum(1 for d in partial_cases if d["predicted_label"] == "correct" and d["confidence"] >= med)
    print(f"\n  Partial cases misclassified as correct: {partial_correct_preds}/{len(partial_cases)}")
    print(f"  Of those, at high confidence: {partial_correct_preds_high_conf}")

    # ── Confidence distribution by ground truth ──────────────────────
    print(f"\n{'='*80}")
    print(f"CONFIDENCE DISTRIBUTION BY GROUND TRUTH")
    print(f"{'='*80}")

    for gt_label in ["correct", "partial", "incorrect"]:
        gt_confs = [d["confidence"] for d in data if d["ground_truth"] == gt_label]
        if not gt_confs:
            continue
        gt_confs_sorted = sorted(gt_confs)
        print(f"\n  {gt_label} (n={len(gt_confs)}):")
        print(f"    Min={min(gt_confs):.2f}  Max={max(gt_confs):.2f}  Median={median(gt_confs):.2f}  Mean={sum(gt_confs)/len(gt_confs):.2f}")
        print(f"    Values: {', '.join(f'{c:.2f}' for c in gt_confs_sorted)}")

    # ── Summary ──────────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")

    delta = p_correct_given_high - p_correct_given_low
    if delta > 0.2:
        assessment = "STRONG SEPARATION — confidence correlates with correctness"
    elif delta > 0.05:
        assessment = "WEAK SEPARATION — narrow range, but direction is correct"
    elif delta > 0:
        assessment = "MINIMAL SEPARATION — confidence barely distinguishes correct from incorrect"
    else:
        assessment = "INVERSE — confidence is anti-correlated with correctness (worst case)"

    print(f"  Median-split delta: {delta:+.1%}")
    print(f"  Assessment: {assessment}")

    if high_conf_errors:
        print(f"\n  ⚠ {len(high_conf_errors)} high-confidence misclassifications found:")
        for d in high_conf_errors:
            print(f"    - {d['case_id']}: GT={d['ground_truth']}, Pred={d['predicted_label']}, Conf={d['confidence']:.2f}")

    # ── Save results ─────────────────────────────────────────────────
    results = {
        "median_confidence": round(med, 4),
        "high_conf_count": len(high_conf),
        "low_conf_count": len(low_conf),
        "p_correct_given_high": round(p_correct_given_high, 4),
        "p_correct_given_low": round(p_correct_given_low, 4),
        "delta_median_split": round(delta, 4),
        "p_error_given_high": round(p_error_given_high, 4),
        "p_error_given_low": round(p_error_given_low, 4),
        "mean_conf_correct_verdict": round(mean_conf_correct, 4),
        "mean_conf_incorrect_verdict": round(mean_conf_incorrect, 4),
        "mean_conf_gt_match": round(mean_conf_gt_match, 4),
        "mean_conf_gt_mismatch": round(mean_conf_gt_mismatch, 4),
        "high_confidence_misclassifications": [
            {"case": d["case_id"], "gt": d["ground_truth"], "pred": d["predicted_label"],
             "conf": d["confidence"]}
            for d in high_conf_errors
        ],
        "partial_misclassified_as_correct": partial_correct_preds,
        "partial_total": len(partial_cases),
        "assessment": assessment,
    }

    output_path = os.path.join(os.path.dirname(__file__), "confidence_correlation_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {output_path}")

    print(f"\n{'='*80}")
    print(f"EXPERIMENT COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
