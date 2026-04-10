"""
Mixed Batch Runner
==================
Combines internal generator cases with external stress sources in configurable ratios.

This allows testing the Doctor with:
1. Pure internal generator cases (baseline)
2. Pure external cases (real-world performance)
3. Mixed batches (realistic stress testing)
4. Gradual distribution shift (testing adaptability)

Usage:
    from external_stress_layer.mixed_batch_runner import MixedBatchRunner
    
    runner = MixedBatchRunner(seed=42)
    
    # Run mixed batch test
    results = runner.run_mixed_test(
        internal_ratio=0.5,  # 50% internal, 50% external
        total_cases=100,
        noise_levels=[0.0, 0.2, 0.4, 0.6],
    )
    
    print(results.summary())
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from external_stress_layer import StressCase, StressKind, StressMetrics, StressTestResult
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.noise_injection_layer import NoiseInjectionLayer
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator


class MixedBatchRunner:
    """Runs mixed batch stress tests combining internal and external sources.

    This is the primary tool for realistic stress testing, allowing:
    - Configurable mix ratios between internal/external cases
    - Gradual distribution shift testing
    - Side-by-side comparison of performance across sources
    """

    def __init__(self, doctor: Any, seed: int = 42):
        """Initialize mixed batch runner.

        Args:
            doctor: The Doctor instance with predict(prompt) -> dict method
            seed: Random seed for reproducibility
        """
        self.doctor = doctor
        self.seed = seed
        self.rng = __import__('random').Random(seed)

        # Initialize components
        self.real_world_injector = RealWorldDataInjector(seed=seed)
        self.noise_layer = NoiseInjectionLayer(seed=seed)
        self.cross_domain_stressor = CrossDomainStressor(seed=seed)
        self.human_attacks = HumanCraftedAttacks(seed=seed)
        self.evaluator = EnhancedEvaluator()

    def run_mixed_test(
        self,
        internal_ratio: float = 0.5,
        total_cases: int = 100,
        noise_levels: Optional[List[float]] = None,
        external_sources: Optional[List[str]] = None,
    ) -> StressTestResult:
        """Run mixed batch stress test.

        Args:
            internal_ratio: Fraction of cases from internal generator (0.0 to 1.0)
            total_cases: Total number of cases to test
            noise_levels: List of noise levels to test (default: [0.0, 0.2, 0.4, 0.6])
            external_sources: Which external sources to use (default: all)
                Options: "real_world", "cross_domain", "human_attacks"

        Returns:
            StressTestResult with comprehensive metrics
        """
        if noise_levels is None:
            noise_levels = [0.0, 0.2, 0.4, 0.6]

        if external_sources is None:
            external_sources = ["real_world", "cross_domain", "human_attacks"]

        print("=" * 60)
        print("MIXED BATCH STRESS TEST")
        print("=" * 60)
        print(f"Total cases: {total_cases}")
        print(f"Internal ratio: {internal_ratio:.0%}")
        print(f"External ratio: {1 - internal_ratio:.0%}")
        print(f"Noise levels: {noise_levels}")

        # Calculate case counts
        internal_count = int(total_cases * internal_ratio)
        external_count = total_cases - internal_count

        # Collect internal cases
        internal_cases = self._generate_internal_cases(internal_count)
        print(f"\n✓ Generated {len(internal_cases)} internal cases")

        # Collect external cases
        external_cases = self._generate_external_cases(external_count, external_sources)
        print(f"✓ Generated {len(external_cases)} external cases")

        # Combine and shuffle
        all_cases = internal_cases + external_cases
        self.rng.shuffle(all_cases)
        print(f"✓ Total: {len(all_cases)} cases")

        # Evaluate at each noise level
        noise_level_results = {}

        for noise_level in noise_levels:
            print(f"\n{'='*60}")
            print(f"Testing at noise level: {noise_level:.1%}")
            print(f"{'='*60}")

            # Apply noise
            cases_at_level = [
                self.noise_layer.apply_noise(case, noise_level)
                for case in all_cases
            ]

            # Run Doctor
            start_time = time.time()
            predictions = []
            for i, case in enumerate(cases_at_level):
                try:
                    prediction = self.doctor.predict(case.prompt)
                    prediction["case_id"] = case.case_id
                    predictions.append(prediction)
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

                if (i + 1) % 20 == 0 or (i + 1) == len(cases_at_level):
                    print(f"  Processed {i + 1}/{len(cases_at_level)} cases...", end="\r")

            elapsed = time.time() - start_time
            print(f"\n  ✓ Completed in {elapsed:.2f}s")

            # Evaluate
            metrics = self.evaluator.evaluate_batch(cases_at_level, predictions)
            noise_level_results[noise_level] = metrics

            print(f"  Accuracy: {metrics.accuracy:.2%}")
            print(f"  Failures: {metrics.failed_cases}/{metrics.total_cases}")

        # Calculate aggregate metrics
        aggregate_metrics = self._calculate_aggregate_metrics(
            noise_level_results,
            all_cases,
            predictions,
        )

        # Build result
        result = StressTestResult(
            metrics=aggregate_metrics,
            cases=all_cases,
            predictions=predictions,
            configuration={
                "seed": self.seed,
                "internal_ratio": internal_ratio,
                "total_cases": total_cases,
                "noise_levels": noise_levels,
                "external_sources": external_sources,
            },
        )

        return result

    def run_distribution_shift_test(
        self,
        total_cases: int = 100,
        internal_ratios: Optional[List[float]] = None,
        noise_level: float = 0.0,
    ) -> Dict[str, Any]:
        """Test performance as distribution shifts from internal to external.

        Args:
            total_cases: Cases per test
            internal_ratios: List of internal ratios to test (default: [1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
            noise_level: Noise level to apply

        Returns:
            Dict with distribution shift analysis
        """
        if internal_ratios is None:
            internal_ratios = [1.0, 0.8, 0.6, 0.4, 0.2, 0.0]

        results = {}

        for ratio in internal_ratios:
            print(f"\n{'='*60}")
            print(f"Testing with internal ratio: {ratio:.0%}")
            print(f"{'='*60}")

            test_result = self.run_mixed_test(
                internal_ratio=ratio,
                total_cases=total_cases,
                noise_levels=[noise_level],
            )

            results[str(ratio)] = {
                "accuracy": test_result.metrics.accuracy,
                "failed_cases": test_result.metrics.failed_cases,
                "total_cases": test_result.metrics.total_cases,
                "by_stress_kind": test_result.metrics.by_stress_kind,
                "failure_patterns": test_result.metrics.failure_patterns,
            }

            print(f"  Accuracy: {test_result.metrics.accuracy:.2%}")

        # Calculate shift impact
        if "1.0" in results and "0.0" in results:
            pure_internal_acc = results["1.0"]["accuracy"]
            pure_external_acc = results["0.0"]["accuracy"]
            drop = pure_internal_acc - pure_external_acc

            results["distribution_shift_analysis"] = {
                "pure_internal_accuracy": pure_internal_acc,
                "pure_external_accuracy": pure_external_acc,
                "accuracy_drop": drop,
                "shift_severity": "severe" if drop > 0.3 else "moderate" if drop > 0.15 else "mild",
            }

        return results

    def run_source_comparison_test(
        self,
        cases_per_source: int = 30,
        noise_level: float = 0.0,
    ) -> Dict[str, Any]:
        """Compare Doctor performance across different sources.

        Args:
            cases_per_source: Cases to test per source
            noise_level: Noise level to apply

        Returns:
            Dict with per-source breakdown
        """
        sources = {
            "internal_generator": lambda: self._generate_internal_cases(cases_per_source),
            "real_world": lambda: self.real_world_injector.generate_cases(cases_per_source),
            "cross_domain": lambda: self.cross_domain_stressor.generate_cases(cases_per_source),
            "human_attacks": lambda: self.human_attacks.generate_cases(),
        }

        results = {}

        for source_name, generator in sources.items():
            print(f"\n{'='*60}")
            print(f"Testing source: {source_name}")
            print(f"{'='*60}")

            cases = generator()
            cases = [self.noise_layer.apply_noise(c, noise_level) for c in cases]

            predictions = []
            for i, case in enumerate(cases):
                try:
                    prediction = self.doctor.predict(case.prompt)
                    prediction["case_id"] = case.case_id
                    predictions.append(prediction)
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

            metrics = self.evaluator.evaluate_batch(cases, predictions)
            results[source_name] = {
                "accuracy": metrics.accuracy,
                "total_cases": metrics.total_cases,
                "failed_cases": metrics.failed_cases,
                "overconfidence_rate": metrics.overconfidence_rate,
                "failure_patterns": metrics.failure_patterns,
            }

            print(f"  Accuracy: {metrics.accuracy:.2%}")
            print(f"  Failures: {metrics.failed_cases}/{metrics.total_cases}")

        return results

    def _generate_internal_cases(self, n: int) -> List[StressCase]:
        """Generate cases from internal adversary (generator)."""
        try:
            from dataset_generator.generator import build_experiment

            # Ensure minimum sizes to avoid division by zero
            baseline_size = max(5, n // 2)
            attack_size = max(5, n // 2)

            experiment = build_experiment(seed=self.seed, baseline_size=baseline_size, attack_size=attack_size)

            cases = []
            case_counter = [0]

            # Baseline cases
            for pub, priv in zip(
                experiment["baseline"]["public_cases"],
                experiment["baseline"]["private_key"].values(),
            ):
                case_counter[0] += 1
                cases.append(StressCase(
                    case_id=f"INT-{case_counter[0]:04d}",
                    prompt=pub["prompt"],
                    stress_kind=StressKind.MIXED,
                    ground_truth=priv["ground_truth"],
                    metadata={
                        "source": "internal_generator",
                        "stratum": priv["stratum"],
                    },
                ))

            # Attack cases
            for pub, priv in zip(
                experiment["attack"]["public_cases"],
                experiment["attack"]["private_key"].values(),
            ):
                case_counter[0] += 1
                cases.append(StressCase(
                    case_id=f"INT-{case_counter[0]:04d}",
                    prompt=pub["prompt"],
                    stress_kind=StressKind.MIXED,
                    ground_truth=priv["ground_truth"],
                    metadata={
                        "source": "internal_generator",
                        "stratum": priv["stratum"],
                        "contradiction": priv.get("contradiction", False),
                        "corrupted_label": priv.get("corrupted_label", False),
                        "signal_inversion": priv.get("signal_inversion", False),
                    },
                ))

            return cases

        except ImportError:
            print("  ⚠ Generator not available, skipping internal cases")
            return []

    def _generate_external_cases(
        self,
        n: int,
        sources: List[str],
    ) -> List[StressCase]:
        """Generate cases from external sources."""
        cases = []

        cases_per_source = max(1, n // len(sources))
        remainder = n - cases_per_source * len(sources)

        for source in sources:
            count = cases_per_source + (1 if remainder > 0 else 0)
            remainder = max(0, remainder - 1)

            if source == "real_world":
                cases.extend(self.real_world_injector.generate_cases(count))
            elif source == "cross_domain":
                cases.extend(self.cross_domain_stressor.generate_cases(count))
            elif source == "human_attacks":
                cases.extend(self.human_attacks.generate_cases())

        return cases

    def _calculate_aggregate_metrics(
        self,
        noise_level_results: Dict[float, StressMetrics],
        cases: List[StressCase],
        predictions: List[Dict[str, Any]],
    ) -> StressMetrics:
        """Calculate aggregate metrics across all noise levels."""
        if not noise_level_results:
            return StressMetrics()

        # Use zero-noise results as base
        base_metrics = noise_level_results.get(0.0, list(noise_level_results.values())[0])

        # Calculate robustness
        clean_acc = base_metrics.accuracy
        noisy_accs = [m.accuracy for level, m in noise_level_results.items() if level > 0]
        avg_noisy_acc = sum(noisy_accs) / len(noisy_accs) if noisy_accs else clean_acc

        robustness = round(avg_noisy_acc / clean_acc, 4) if clean_acc > 0 else 0.0

        # Aggregate failure patterns
        all_failures = {}
        for metrics in noise_level_results.values():
            for pattern, count in metrics.failure_patterns.items():
                all_failures[pattern] = all_failures.get(pattern, 0) + count

        # Combine by stress kind
        combined_by_kind = {}
        for metrics in noise_level_results.values():
            for kind, kind_metrics in metrics.by_stress_kind.items():
                if kind not in combined_by_kind:
                    combined_by_kind[kind] = {"correct": 0, "total": 0}
                combined_by_kind[kind]["correct"] += kind_metrics.get("correct", 0)
                combined_by_kind[kind]["total"] += kind_metrics.get("total", 0)

        by_kind_accuracy = {
            kind: round(data["correct"] / data["total"], 4) if data["total"] > 0 else 0.0
            for kind, data in combined_by_kind.items()
        }

        # Degradation curve
        degradation_curve = {
            str(level): metrics.accuracy
            for level, metrics in sorted(noise_level_results.items())
        }

        return StressMetrics(
            accuracy=base_metrics.accuracy,
            overconfidence_rate=base_metrics.overconfidence_rate,
            underconfidence_rate=base_metrics.underconfidence_rate,
            robustness_score=robustness,
            degradation_curve=degradation_curve,
            failure_diversity=base_metrics.failure_diversity,
            recovery_rate=0.0,
            by_stress_kind=by_kind_accuracy,
            failure_patterns=all_failures,
            failure_by_stratum=base_metrics.failure_by_stratum,
            total_cases=base_metrics.total_cases,
            correct_cases=base_metrics.correct_cases,
            failed_cases=base_metrics.failed_cases,
        )
