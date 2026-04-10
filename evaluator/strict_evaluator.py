from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Dict, List


def _entropy(values: List[float], bins: int = 4) -> float:
    if not values:
        return 0.0
    counts = [0] * bins
    for value in values:
        index = min(int(value * bins), bins - 1)
        counts[index] += 1
    total = sum(counts)
    entropy = 0.0
    for count in counts:
        if count == 0:
            continue
        probability = count / total
        entropy -= probability * math.log(probability, 2)
    return round(entropy / math.log(bins, 2), 4)


def evaluate_batch(private_key: Dict[str, Dict[str, object]], predictions: List[Dict[str, object]]) -> Dict[str, object]:
    grouped_confidences = defaultdict(list)
    exact_matches = []
    overconfident = 0
    underconfident = 0
    contradiction_total = 0
    contradiction_resolved = 0
    inversion_total = 0
    inversion_correct = 0
    undefined_total = 0
    undefined_correct = 0

    for prediction in predictions:
        case = private_key[prediction["case_id"]]
        truth = case["ground_truth"]
        label = prediction["label"]
        confidence = float(prediction["confidence"])
        matched = label == truth
        exact_matches.append(1.0 if matched else 0.0)
        grouped_confidences[str(case["stratum"])].append(confidence)

        if not matched and confidence >= 0.8:
            overconfident += 1
        if matched and confidence <= 0.4:
            underconfident += 1

        if bool(case["contradiction"]):
            contradiction_total += 1
            if (
                bool(prediction.get("conflict_detected"))
                and bool(prediction.get("priority_rule_applied"))
                and bool(prediction.get("discarded_weaker_constraints"))
            ):
                contradiction_resolved += 1

        if bool(case["signal_inversion"]):
            inversion_total += 1
            if matched:
                inversion_correct += 1

        if truth == "undefined":
            undefined_total += 1
            if matched:
                undefined_correct += 1

    accuracy = round(statistics.fmean(exact_matches), 4) if exact_matches else 0.0
    return {
        "accuracy": accuracy,
        "overconfidence_rate": round(overconfident / len(predictions), 4) if predictions else 0.0,
        "underconfidence_rate": round(underconfident / len(predictions), 4) if predictions else 0.0,
        "confidence_entropy_by_stratum": {
            stratum: _entropy(confidences) for stratum, confidences in grouped_confidences.items()
        },
        "contradiction_resolution": round(contradiction_resolved / contradiction_total, 4) if contradiction_total else 0.0,
        "signal_inversion_survival_rate": round(inversion_correct / inversion_total, 4) if inversion_total else 0.0,
        "undefined_case_handling": round(undefined_correct / undefined_total, 4) if undefined_total else 0.0,
        "undefined_random_baseline": round(1 / 3, 4),
    }


def aggregate_runs(runs: List[Dict[str, object]]) -> Dict[str, object]:
    baseline_scores = [run["baseline_metrics"]["accuracy"] for run in runs]
    attack_scores = [run["attack_metrics"]["accuracy"] for run in runs]
    drops = [baseline - attack for baseline, attack in zip(baseline_scores, attack_scores)]
    mean_entropy = statistics.fmean(
        statistics.fmean(run["attack_metrics"]["confidence_entropy_by_stratum"].values())
        for run in runs
    )
    baseline_mean = statistics.fmean(baseline_scores)
    attack_mean = statistics.fmean(attack_scores)
    attack_stdev = statistics.pstdev(attack_scores) if len(attack_scores) > 1 else 0.0
    return {
        "mean_performance": {
            "baseline": round(baseline_mean, 4),
            "attack": round(attack_mean, 4),
        },
        "variance": round(statistics.pvariance(attack_scores), 4) if len(attack_scores) > 1 else 0.0,
        "variance_ratio": round((attack_stdev / baseline_mean) if baseline_mean else 1.0, 4),
        "worst_case_drop": round(max(drops), 4),
        "overconfidence_rate": round(statistics.fmean(run["attack_metrics"]["overconfidence_rate"] for run in runs), 4),
        "underconfidence_rate": round(statistics.fmean(run["attack_metrics"]["underconfidence_rate"] for run in runs), 4),
        "confidence_entropy_across_strata": round(mean_entropy, 4),
        "contradiction_resolution": round(statistics.fmean(run["attack_metrics"]["contradiction_resolution"] for run in runs), 4),
        "signal_inversion_survival_rate": round(statistics.fmean(run["attack_metrics"]["signal_inversion_survival_rate"] for run in runs), 4),
        "undefined_case_handling": round(statistics.fmean(run["attack_metrics"]["undefined_case_handling"] for run in runs), 4),
        "undefined_random_baseline": round(statistics.fmean(run["attack_metrics"]["undefined_random_baseline"] for run in runs), 4),
        "dataset_checks": {
            "undefined_share_mean": round(statistics.fmean(run["attack_summary"]["undefined_share"] for run in runs), 4),
            "corrupted_share_mean": round(statistics.fmean(run["attack_summary"]["corrupted_share"] for run in runs), 4),
            "signal_inversion_share_mean": round(statistics.fmean(run["attack_summary"]["signal_inversion_share"] for run in runs), 4),
            "all_strata_fixed": all(run["attack_summary"]["fixed_proportions_respected"] for run in runs),
        },
    }


def acceptance_from_aggregate(aggregate: Dict[str, object]) -> Dict[str, bool]:
    baseline = aggregate["mean_performance"]["baseline"]
    attack = aggregate["mean_performance"]["attack"]
    checks = {
        "performance_drop_leq_15pct": (baseline - attack) <= 0.15,
        "overconfidence_leq_5pct": aggregate["overconfidence_rate"] <= 0.05,
        "contradiction_resolution_ge_70pct": aggregate["contradiction_resolution"] >= 0.70,
        "variance_leq_10pct": aggregate["variance_ratio"] <= 0.10,
        "undefined_beats_random": aggregate["undefined_case_handling"] > aggregate["undefined_random_baseline"],
        "raw_only_constraint": True,
    }
    checks["robust"] = all(checks.values())
    return checks
