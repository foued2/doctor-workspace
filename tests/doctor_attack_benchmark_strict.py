"""
Strict raw-only benchmark orchestrator.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from dataset_generator import DEFAULT_SEEDS, build_experiment
from doctor import RawPromptDoctor
from evaluator import acceptance_from_aggregate, aggregate_runs, evaluate_batch

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"


def _predict_batch(doctor: RawPromptDoctor, public_cases: List[Dict[str, str]]) -> List[Dict[str, object]]:
    predictions = []
    for case in public_cases:
        prediction = doctor.predict(case["prompt"])
        predictions.append(
            {
                "case_id": case["case_id"],
                "label": prediction["label"],
                "confidence": prediction["confidence"],
                "conflict_detected": prediction["conflict_detected"],
                "priority_rule_applied": prediction["priority_rule_applied"],
                "discarded_weaker_constraints": prediction["discarded_weaker_constraints"],
            }
        )
    return predictions


def run_seed(seed: int, baseline_size: int, attack_size: int) -> Dict[str, object]:
    experiment = build_experiment(seed, baseline_size, attack_size)
    doctor = RawPromptDoctor()

    baseline_predictions = _predict_batch(doctor, experiment["baseline"]["public_cases"])
    attack_predictions = _predict_batch(doctor, experiment["attack"]["public_cases"])

    return {
        "seed": seed,
        "baseline_summary": experiment["baseline"]["summary"],
        "attack_summary": experiment["attack"]["summary"],
        "baseline_metrics": evaluate_batch(experiment["baseline"]["private_key"], baseline_predictions),
        "attack_metrics": evaluate_batch(experiment["attack"]["private_key"], attack_predictions),
    }


def run_benchmark(baseline_size: int, attack_size: int, seeds: List[int]) -> Dict[str, object]:
    runs = [run_seed(seed, baseline_size, attack_size) for seed in seeds]
    aggregate = aggregate_runs(runs)
    acceptance = acceptance_from_aggregate(aggregate)
    return {
        "generated_at": datetime.now().isoformat(),
        "baseline_size": baseline_size,
        "attack_size": attack_size,
        "seed_count": len(seeds),
        "seeds": seeds,
        "runs": runs,
        "aggregate": aggregate,
        "acceptance": acceptance,
    }


def print_outcome(result: Dict[str, object], report_path: Path) -> None:
    aggregate = result["aggregate"]
    acceptance = result["acceptance"]
    print("STRICT DOCTOR ATTACK OUTCOME")
    print(f"report={report_path}")
    print(f"seed_count={result['seed_count']}")
    print("raw_only_constraint=pass")
    print(f"baseline_mean_accuracy={aggregate['mean_performance']['baseline']:.4f}")
    print(f"attack_mean_accuracy={aggregate['mean_performance']['attack']:.4f}")
    print(f"worst_case_drop={aggregate['worst_case_drop']:.4f}")
    print(f"variance={aggregate['variance']:.4f}")
    print(f"variance_ratio={aggregate['variance_ratio']:.4f}")
    print(f"overconfidence_rate={aggregate['overconfidence_rate']:.4f}")
    print(f"underconfidence_rate={aggregate['underconfidence_rate']:.4f}")
    print(f"confidence_entropy_across_strata={aggregate['confidence_entropy_across_strata']:.4f}")
    print(f"contradiction_resolution={aggregate['contradiction_resolution']:.4f}")
    print(f"signal_inversion_survival_rate={aggregate['signal_inversion_survival_rate']:.4f}")
    print(f"undefined_case_handling={aggregate['undefined_case_handling']:.4f}")
    print(f"undefined_random_baseline={aggregate['undefined_random_baseline']:.4f}")
    print(f"undefined_share_mean={aggregate['dataset_checks']['undefined_share_mean']:.4f}")
    print(f"corrupted_share_mean={aggregate['dataset_checks']['corrupted_share_mean']:.4f}")
    print(f"signal_inversion_share_mean={aggregate['dataset_checks']['signal_inversion_share_mean']:.4f}")
    print(f"all_strata_fixed={aggregate['dataset_checks']['all_strata_fixed']}")
    print(f"robust={acceptance['robust']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Strict raw-only attack benchmark.")
    parser.add_argument("--baseline", type=int, default=120)
    parser.add_argument("--attack", type=int, default=250)
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    result = run_benchmark(args.baseline, args.attack, DEFAULT_SEEDS)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"doctor_attack_benchmark_strict_{stamp}.json"
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print_outcome(result, report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
