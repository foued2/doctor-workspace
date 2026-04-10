"""
Stress Test Orchestrator
========================
Combines all External Stress Layer components into a unified testing pipeline.

Architecture:
  Adaptive Generator (internal adversary)
          +
  External Stress Layer (uncontrolled inputs)
    - RealWorldInjector
    - NoiseInjectionLayer
    - CrossDomainStressor
    - HumanCraftedAttacks
          ↓
      Doctor
          ↓
  Enhanced Evaluator

Usage:
    from external_stress_layer import StressTestOrchestrator
    from doctor.llm_doctor import LLMDoctor as RawPromptDoctor
    
    orchestrator = StressTestOrchestrator(doctor=RawPromptDoctor())
    
    # Run comprehensive stress test
    results = orchestrator.run_stress_test(
        n_external=50,
        noise_levels=[0.0, 0.2, 0.4, 0.6],
        include_generator=True,
    )
    
    print(results.summary())
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from external_stress_layer import StressKind, StressCase, StressMetrics, StressTestResult
from external_stress_layer.real_world_injector import RealWorldInjector
from external_stress_layer.noise_injection_layer import NoiseInjectionLayer
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator


class StressTestOrchestrator:
    """Orchestrates comprehensive stress testing of the Doctor.
    
    Combines internal (generator) and external stress sources,
    applies noise corruption, and evaluates with extended metrics.
    """
    
    def __init__(
        self,
        doctor: Any,  # RawPromptDoctor or compatible
        seed: int = 42,
    ):
        """Initialize orchestrator.
        
        Args:
            doctor: The Doctor instance with predict(prompt) -> dict method
            seed: Random seed for reproducibility
        """
        self.doctor = doctor
        self.seed = seed
        
        # Initialize components
        self.real_world_injector = RealWorldInjector(seed=seed)
        self.noise_layer = NoiseInjectionLayer(seed=seed)
        self.cross_domain_stressor = CrossDomainStressor(seed=seed)
        self.human_attacks = HumanCraftedAttacks(seed=seed)
        self.evaluator = EnhancedEvaluator()
    
    def run_stress_test(
        self,
        n_external: int = 50,
        noise_levels: Optional[List[float]] = None,
        include_generator: bool = True,
        include_real_world: bool = True,
        include_cross_domain: bool = True,
        include_human_attacks: bool = True,
        generator_cases: Optional[List[StressCase]] = None,
    ) -> StressTestResult:
        """Run comprehensive stress test.
        
        Args:
            n_external: Number of external cases per source
            noise_levels: List of noise levels to test (default: [0.0, 0.2, 0.4, 0.6])
            include_generator: Include synthetic generator cases
            include_real_world: Include real-world problems
            include_cross_domain: Include cross-domain cases
            include_human_attacks: Include human-crafted attacks
            generator_cases: Pre-generated cases (if not using internal generator)
            
        Returns:
            StressTestResult with comprehensive metrics
        """
        if noise_levels is None:
            noise_levels = [0.0, 0.2, 0.4, 0.6]
        
        print("=" * 60)
        print("STRESS TEST INITIALIZATION")
        print("=" * 60)
        
        # Collect cases from all sources
        all_cases = []
        configuration = {
            "seed": self.seed,
            "noise_levels": noise_levels,
            "sources": {},
        }
        
        # Internal generator cases
        if include_generator and generator_cases is None:
            print("\n[1/4] Generating internal adversary cases...")
            generator_cases = self._generate_internal_cases(n_external)
        
        if generator_cases:
            all_cases.extend(generator_cases)
            configuration["sources"]["generator"] = len(generator_cases)
            print(f"  ✓ {len(generator_cases)} generator cases")
        
        # Real-world injection
        if include_real_world:
            print("\n[2/4] Injecting real-world problems...")
            rw_cases = self.real_world_injector.generate_cases(n_external // 2)
            all_cases.extend(rw_cases)
            configuration["sources"]["real_world"] = len(rw_cases)
            print(f"  ✓ {len(rw_cases)} real-world cases")
        
        # Cross-domain stress
        if include_cross_domain:
            print("\n[3/4] Generating cross-domain cases...")
            cd_cases = self.cross_domain_stressor.generate_cases(n_external // 2)
            all_cases.extend(cd_cases)
            configuration["sources"]["cross_domain"] = len(cd_cases)
            print(f"  ✓ {len(cd_cases)} cross-domain cases")
        
        # Human-crafted attacks
        if include_human_attacks:
            print("\n[4/4] Loading human-crafted attacks...")
            hc_cases = self.human_attacks.generate_cases()
            all_cases.extend(hc_cases)
            configuration["sources"]["human_crafted"] = len(hc_cases)
            print(f"  ✓ {len(hc_cases)} human-crafted cases")
        
        print(f"\n{'='*60}")
        print(f"TOTAL CASES: {len(all_cases)}")
        print(f"{'='*60}")
        
        # Evaluate at each noise level
        all_predictions = []
        all_cases_noised = []
        noise_level_results = {}
        
        for noise_level in noise_levels:
            print(f"\n{'='*60}")
            print(f"TESTING AT NOISE LEVEL: {noise_level:.1%}")
            print(f"{'='*60}")
            
            # Apply noise to cases (skip for non-applicable stress kinds)
            cases_at_level = []
            for case in all_cases:
                if case.stress_kind == StressKind.NOISE_INJECTION or noise_level > 0:
                    noised_case = self.noise_layer.apply_noise(case, noise_level)
                    cases_at_level.append(noised_case)
                else:
                    cases_at_level.append(case)
            
            # Run Doctor on all cases
            start_time = time.time()
            predictions = []
            for i, case in enumerate(cases_at_level):
                try:
                    prediction = self.doctor.predict(case.prompt)
                    prediction["case_id"] = case.case_id
                    predictions.append(prediction)
                except Exception as e:
                    # Handle Doctor crashes gracefully
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
                
                if (i + 1) % 10 == 0 or (i + 1) == len(cases_at_level):
                    print(f"  Processed {i + 1}/{len(cases_at_level)} cases...", end="\r")
            
            elapsed = time.time() - start_time
            print(f"\n  ✓ Completed in {elapsed:.2f}s")
            
            # Evaluate
            metrics = self.evaluator.evaluate_batch(cases_at_level, predictions)
            noise_level_results[noise_level] = metrics
            
            print(f"  Accuracy: {metrics.accuracy:.2%}")
            print(f"  Failures: {metrics.failed_cases}/{metrics.total_cases}")
            
            # Store for aggregate analysis
            if noise_level == 0.0:
                all_predictions = predictions
                all_cases_noised = cases_at_level
        
        # Calculate aggregate metrics
        print(f"\n{'='*60}")
        print("CALCULATING AGGREGATE METRICS")
        print(f"{'='*60}")
        
        aggregate_metrics = self._calculate_aggregate_metrics(
            noise_level_results,
            all_cases_noised,
            all_predictions,
        )
        
        # Build result
        result = StressTestResult(
            metrics=aggregate_metrics,
            cases=all_cases_noised,
            predictions=all_predictions,
            configuration=configuration,
        )
        
        return result
    
    def run_degradation_analysis(
        self,
        base_cases: Optional[List[StressCase]] = None,
        noise_levels: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Run detailed degradation curve analysis.
        
        Args:
            base_cases: Cases to test (default: generate mixed batch)
            noise_levels: Noise levels to test
            
        Returns:
            Dict with degradation curve data
        """
        if noise_levels is None:
            noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        
        if base_cases is None:
            base_cases = self.real_world_injector.generate_cases(20)
        
        # Apply noise at each level and evaluate
        cases_by_noise = {}
        for level in noise_levels:
            cases_at_level = [self.noise_layer.apply_noise(c, level) for c in base_cases]
            predictions = [self.doctor.predict(c.prompt) for c in cases_at_level]
            cases_by_noise[level] = (cases_at_level, predictions)
        
        return self.evaluator.evaluate_degradation_curve(cases_by_noise)
    
    def run_recovery_test(
        self,
        cases: Optional[List[StressCase]] = None,
        n_retries: int = 1,
    ) -> Dict[str, Any]:
        """Test Doctor's ability to recover from failures.
        
        Args:
            cases: Cases to test
            n_retries: Number of retry attempts
            
        Returns:
            Recovery metrics
        """
        if cases is None:
            cases = self.human_attacks.generate_cases()
        
        # Initial attempt
        initial_predictions = [self.doctor.predict(c.prompt) for c in cases]
        
        # Retry failed cases (in real scenario, might add hints/context)
        failed_indices = [
            i for i, (c, p) in enumerate(zip(cases, initial_predictions))
            if p["label"] != c.ground_truth
        ]
        
        if not failed_indices:
            return {"initial_failures": 0, "recovery_rate": 1.0}
        
        # Retry with same prompts (tests consistency)
        retry_predictions = list(initial_predictions)
        for idx in failed_indices:
            retry_predictions[idx] = self.doctor.predict(cases[idx].prompt)
        
        return self.evaluator.evaluate_recovery(
            initial_predictions,
            retry_predictions,
            cases,
        )
    
    def get_attack_catalog(self) -> List[Dict[str, str]]:
        """Get catalog of available human-crafted attacks."""
        return self.human_attacks.list_attacks()
    
    def _generate_internal_cases(self, n: int) -> List[StressCase]:
        """Generate cases from internal adversary (generator)."""
        try:
            from dataset_generator.adaptive_generator import AdaptiveGenerator
            from dataset_generator.generator import build_experiment
            
            # Use static generator for baseline
            experiment = build_experiment(seed=self.seed, baseline_size=n // 2, attack_size=n // 2)
            
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
            recovery_rate=0.0,  # Not tested in standard run
            by_stress_kind=by_kind_accuracy,
            failure_patterns=all_failures,
            failure_by_stratum=base_metrics.failure_by_stratum,
            total_cases=base_metrics.total_cases,
            correct_cases=base_metrics.correct_cases,
            failed_cases=base_metrics.failed_cases,
        )
