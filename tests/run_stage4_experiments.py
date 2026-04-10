"""
Controlled Experiments — Stage 4
=================================
Runs three experiments:
1. Baseline (no ESL) — Internal generator only
2. ESL only — External stress sources only
3. Mixed — 50/50 internal + external

Reports:
- Accuracy per experiment
- Confusion matrix (critical: shows classification behavior)
- Calibration curves (confidence vs. correctness)
- Per-label F1 scores
- Comparison of failure patterns across experiments

Usage:
    python tests/run_stage4_experiments.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from doctor.raw_prompt_doctor import RawPromptDoctor
from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.noise_injection_layer import NoiseInjectionLayer
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks


def generate_baseline_cases(n: int = 60, seed: int = 42) -> List[StressCase]:
    """Generate internal generator cases for baseline."""
    from dataset_generator.generator import build_experiment

    baseline_size = max(10, n // 2)
    attack_size = max(10, n // 2)
    experiment = build_experiment(seed=seed, baseline_size=baseline_size, attack_size=attack_size)

    cases = []
    counter = [0]

    for pub, priv in zip(
        experiment["baseline"]["public_cases"],
        experiment["baseline"]["private_key"].values(),
    ):
        counter[0] += 1
        cases.append(StressCase(
            case_id=f"INT-{counter[0]:04d}",
            prompt=pub["prompt"],
            stress_kind=StressKind.MIXED,
            ground_truth=priv["ground_truth"],
            metadata={"source": "baseline", "stratum": priv["stratum"]},
        ))

    for pub, priv in zip(
        experiment["attack"]["public_cases"],
        experiment["attack"]["private_key"].values(),
    ):
        counter[0] += 1
        cases.append(StressCase(
            case_id=f"INT-{counter[0]:04d}",
            prompt=pub["prompt"],
            stress_kind=StressKind.MIXED,
            ground_truth=priv["ground_truth"],
            metadata={"source": "attack", "stratum": priv["stratum"]},
        ))

    return cases


def generate_esl_cases(n: int = 60, seed: int = 42) -> List[StressCase]:
    """Generate external stress layer cases."""
    cases = []

    rw = RealWorldDataInjector(seed=seed)
    cd = CrossDomainStressor(seed=seed)
    hc = HumanCraftedAttacks(seed=seed)

    cases.extend(rw.generate_cases(n // 3))
    cases.extend(cd.generate_cases(n // 3))
    cases.extend(hc.generate_cases())

    return cases


def generate_mixed_cases(n: int = 60, seed: int = 42) -> List[StressCase]:
    """Generate mixed 50/50 internal + external cases."""
    internal = generate_baseline_cases(n // 2, seed)
    external = generate_esl_cases(n // 2, seed)
    return internal + external


def run_experiment(name: str, cases: List[StressCase], doctor: RawPromptDoctor) -> Dict[str, Any]:
    """Run a single experiment and collect results."""
    print(f"\n{'='*80}")
    print(f"EXPERIMENT: {name}")
    print(f"{'='*80}")
    print(f"Total cases: {len(cases)}")

    predictions = []
    for i, case in enumerate(cases):
        try:
            pred = doctor.predict(case.prompt)
            pred["case_id"] = case.case_id
            predictions.append(pred)
        except Exception as e:
            predictions.append({
                "case_id": case.case_id,
                "label": "undefined",
                "confidence": 0.5,
                "conflict_detected": False,
                "priority_rule_applied": False,
                "discarded_weaker_constraints": False,
                "kept_constraints": [],
                "discarded_constraints": [],
                "decision_path": ["error"],
                "system_bias_indicators": {},
                "error": str(e),
            })

        if (i + 1) % 20 == 0 or (i + 1) == len(cases):
            print(f"  Processed {i + 1}/{len(cases)} cases...", end="\r")

    print(f"\n  ✓ Completed")

    # Compute metrics
    labels = ["correct", "partial", "undefined"]
    confusion = {gt: {pred: 0 for pred in labels} for gt in labels}
    correct = 0
    confidence_correct = []
    confidence_incorrect = []

    for case, pred in zip(cases, predictions):
        gt = case.ground_truth
        pl = pred["label"]
        conf = float(pred.get("confidence", 0.5))

        if gt in confusion and pl in confusion[gt]:
            confusion[gt][pl] += 1

        matched = gt == pl
        if matched:
            correct += 1
            confidence_correct.append(conf)
        else:
            confidence_incorrect.append(conf)

    accuracy = correct / len(cases) if cases else 0.0

    # Per-label metrics
    per_label = {}
    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[gt][label] for gt in labels if gt != label)
        fn = sum(confusion[label][pred] for pred in labels if pred != label)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        per_label[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": sum(confusion[label].values()),
        }

    # Confidence calibration
    avg_conf_correct = sum(confidence_correct) / len(confidence_correct) if confidence_correct else 0.0
    avg_conf_incorrect = sum(confidence_incorrect) / len(confidence_incorrect) if confidence_incorrect else 0.0

    return {
        "name": name,
        "total_cases": len(cases),
        "accuracy": round(accuracy, 4),
        "correct": correct,
        "incorrect": len(cases) - correct,
        "confusion_matrix": confusion,
        "per_label": per_label,
        "avg_confidence_correct": round(avg_conf_correct, 4),
        "avg_confidence_incorrect": round(avg_conf_incorrect, 4),
        "predictions": predictions,
        "cases": cases,
    }


def print_confusion_matrix(confusion: Dict[str, Dict[str, int]], title: str):
    """Pretty print confusion matrix."""
    labels = ["correct", "partial", "undefined"]

    print(f"\n  Confusion Matrix — {title}")
    print(f"  {'Predicted →':^35}")
    print(f"  {'Actual ↓':>12} | {'correct':>8} | {'partial':>8} | {'undefined':>10} | Total")
    print(f"  {'-'*12}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}-+-{'-'*5}")

    for gt in labels:
        row = confusion[gt]
        total = sum(row.values())
        print(f"  {gt:>12} | {row['correct']:>8} | {row['partial']:>8} | {row['undefined']:>10} | {total:>5}")

    # Column totals
    col_totals = {pred: sum(confusion[gt][pred] for gt in labels) for pred in labels}
    grand_total = sum(col_totals.values())
    print(f"  {'-'*12}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}-+-{'-'*5}")
    print(f"  {'Total':>12} | {col_totals['correct']:>8} | {col_totals['partial']:>8} | {col_totals['undefined']:>10} | {grand_total:>5}")


def print_calibration_curve(results: Dict[str, Any]):
    """Print confidence calibration info."""
    print(f"\n  Confidence Calibration:")
    print(f"    Avg confidence (correct cases):   {results['avg_confidence_correct']:.4f}")
    print(f"    Avg confidence (incorrect cases): {results['avg_confidence_incorrect']:.4f}")
    separation = results['avg_confidence_correct'] - results['avg_confidence_incorrect']
    print(f"    Separation: {separation:.4f} {'✓' if separation > 0.1 else '⚠'}")


def main():
    print("=" * 80)
    print("STAGE 4 CONTROLLED EXPERIMENTS")
    print("=" * 80)

    doctor = RawPromptDoctor()

    # =========================================================================
    # Experiment 1: Baseline (no ESL)
    # =========================================================================
    print("\n" + "=" * 80)
    print("EXPERIMENT 1: BASELINE (Internal Generator Only)")
    print("=" * 80)

    baseline_cases = generate_baseline_cases(n=60, seed=42)
    baseline_results = run_experiment("baseline", baseline_cases, doctor)

    print(f"\n  Accuracy: {baseline_results['accuracy']:.2%} ({baseline_results['correct']}/{baseline_results['total_cases']})")
    print_confusion_matrix(baseline_results["confusion_matrix"], "Baseline")
    print_calibration_curve(baseline_results)

    print(f"\n  Per-Label F1:")
    for label, metrics in baseline_results["per_label"].items():
        print(f"    {label}: F1={metrics['f1']:.4f} (P={metrics['precision']:.4f}, R={metrics['recall']:.4f}, N={metrics['support']})")

    # =========================================================================
    # Experiment 2: ESL Only
    # =========================================================================
    print("\n" + "=" * 80)
    print("EXPERIMENT 2: ESL ONLY (External Stress Layer)")
    print("=" * 80)

    esl_cases = generate_esl_cases(n=60, seed=42)
    esl_results = run_experiment("esl_only", esl_cases, doctor)

    print(f"\n  Accuracy: {esl_results['accuracy']:.2%} ({esl_results['correct']}/{esl_results['total_cases']})")
    print_confusion_matrix(esl_results["confusion_matrix"], "ESL Only")
    print_calibration_curve(esl_results)

    print(f"\n  Per-Label F1:")
    for label, metrics in esl_results["per_label"].items():
        print(f"    {label}: F1={metrics['f1']:.4f} (P={metrics['precision']:.4f}, R={metrics['recall']:.4f}, N={metrics['support']})")

    # =========================================================================
    # Experiment 3: Mixed (50/50)
    # =========================================================================
    print("\n" + "=" * 80)
    print("EXPERIMENT 3: MIXED (50/50 Internal + External)")
    print("=" * 80)

    mixed_cases = generate_mixed_cases(n=100, seed=42)
    mixed_results = run_experiment("mixed", mixed_cases, doctor)

    print(f"\n  Accuracy: {mixed_results['accuracy']:.2%} ({mixed_results['correct']}/{mixed_results['total_cases']})")
    print_confusion_matrix(mixed_results["confusion_matrix"], "Mixed 50/50")
    print_calibration_curve(mixed_results)

    print(f"\n  Per-Label F1:")
    for label, metrics in mixed_results["per_label"].items():
        print(f"    {label}: F1={metrics['f1']:.4f} (P={metrics['precision']:.4f}, R={metrics['recall']:.4f}, N={metrics['support']})")

    # =========================================================================
    # Comparison
    # =========================================================================
    print("\n" + "=" * 80)
    print("COMPARISON ACROSS EXPERIMENTS")
    print("=" * 80)

    experiments = [
        ("Baseline", baseline_results),
        ("ESL Only", esl_results),
        ("Mixed 50/50", mixed_results),
    ]

    print(f"\n  {'Experiment':<18} {'Accuracy':>10} {'Correct':>10} {'Incorrect':>10} {'Conf(Correct)':>15} {'Conf(Incorrect)':>15}")
    print(f"  {'-'*18} {'-'*10} {'-'*10} {'-'*10} {'-'*15} {'-'*15}")

    for name, results in experiments:
        print(
            f"  {name:<18} | {results['accuracy']:>9.2%} | {results['correct']:>9} | "
            f"{results['incorrect']:>9} | {results['avg_confidence_correct']:>14.4f} | "
            f"{results['avg_confidence_incorrect']:>14.4f}"
        )

    # Confusion matrix comparison
    print(f"\n  {'='*80}")
    print(f"  CONFUSION MATRIX COMPARISON")
    print(f"  {'='*80}")

    for name, results in experiments:
        print_confusion_matrix(results["confusion_matrix"], name)

    # Per-label F1 comparison
    print(f"\n  {'='*80}")
    print(f"  PER-LABEL F1 COMPARISON")
    print(f"  {'='*80}")

    labels = ["correct", "partial", "undefined"]
    print(f"\n  {'Experiment':<18} {'F1(correct)':>14} {'F1(partial)':>14} {'F1(undefined)':>14}")
    print(f"  {'-'*18} {'-'*14} {'-'*14} {'-'*14}")

    for name, results in experiments:
        f1_correct = results["per_label"]["correct"]["f1"]
        f1_partial = results["per_label"]["partial"]["f1"]
        f1_undefined = results["per_label"]["undefined"]["f1"]
        print(
            f"  {name:<18} | {f1_correct:>13.4f} | {f1_partial:>13.4f} | {f1_undefined:>13.4f}"
        )

    # =========================================================================
    # Key Findings
    # =========================================================================
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)

    # Baseline vs ESL gap
    baseline_acc = baseline_results["accuracy"]
    esl_acc = esl_results["accuracy"]
    mixed_acc = mixed_results["accuracy"]

    print(f"\n1. Baseline accuracy: {baseline_acc:.2%}")
    print(f"   ESL accuracy:       {esl_acc:.2%}")
    print(f"   Mixed accuracy:     {mixed_acc:.2%}")

    if esl_acc > baseline_acc:
        print(f"   → External cases are EASIER than internal generator cases (+{(esl_acc - baseline_acc):.2%})")
    elif esl_acc < baseline_acc:
        print(f"   → External cases are HARDER than internal generator cases (-{(baseline_acc - esl_acc):.2%})")
    else:
        print(f"   → External and internal cases have equal difficulty")

    # Calibration
    print(f"\n2. Calibration quality:")
    for name, results in experiments:
        sep = results["avg_confidence_correct"] - results["avg_confidence_incorrect"]
        status = "✓ Good" if sep > 0.15 else "⚠ Poor" if sep > 0.05 else "✗ Bad"
        print(f"   {name:<18}: Separation={sep:.4f} ({status})")

    # Undefined detection
    print(f"\n3. Undefined detection:")
    for name, results in experiments:
        cm = results["confusion_matrix"]
        undefined_gt = cm.get("undefined", {})
        total_undefined = sum(undefined_gt.values()) if undefined_gt else 0
        correctly_undefined = undefined_gt.get("undefined", 0) if undefined_gt else 0
        recall_undefined = correctly_undefined / total_undefined if total_undefined > 0 else 0.0
        print(f"   {name:<18}: Undefined recall = {recall_undefined:.2%} ({correctly_undefined}/{total_undefined})")

    # Failure mode analysis
    print(f"\n4. Dominant failure modes (Mixed experiment):")
    cm = mixed_results["confusion_matrix"]
    for gt in ["correct", "partial", "undefined"]:
        misclassifications = {pred: count for pred, count in cm[gt].items() if pred != gt and count > 0}
        if misclassifications:
            total_mis = sum(misclassifications.values())
            print(f"   Ground truth '{gt}' ({total_mis} misclassifications):")
            for pred, count in sorted(misclassifications.items(), key=lambda x: -x[1]):
                pct = count / total_mis
                print(f"     → classified as '{pred}': {count} ({pct:.0%})")

    print("\n" + "=" * 80)
    print("✓ EXPERIMENTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
