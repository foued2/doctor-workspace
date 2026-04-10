"""
External Stress Test Dashboard
===============================
Comprehensive stress testing with all ESL components.

This script runs:
1. Mixed batch tests with configurable ratios
2. Distribution shift analysis
3. Source comparison tests
4. Degradation curve analysis
5. Human attack catalog review
6. Detailed failure analysis

Usage:
    python tests/run_stress_dashboard.py
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from doctor.raw_prompt_doctor import RawPromptDoctor
from external_stress_layer.mixed_batch_runner import MixedBatchRunner
from external_stress_layer import (
    StressTestOrchestrator,
    RealWorldDataInjector,
    NoiseInjectionLayer,
    CrossDomainStressor,
    HumanCraftedAttacks,
)


def main():
    print("=" * 80)
    print("EXTERNAL STRESS TEST DASHBOARD")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Initialize Doctor
    doctor = RawPromptDoctor()

    # Initialize runner
    runner = MixedBatchRunner(doctor=doctor, seed=42)

    # =========================================================================
    # 1. Human-Crafted Attack Catalog Review
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 1: HUMAN-CRAFTED ATTACK CATALOG")
    print("=" * 80)

    human_attacks = HumanCraftedAttacks(seed=42)
    attacks = human_attacks.list_attacks()

    print(f"\nTotal attack patterns: {len(attacks)}")
    for i, attack in enumerate(attacks, 1):
        print(f"\n{i}. {attack['name']}")
        print(f"   Description: {attack['description'][:80]}...")
        print(f"   Target: {attack['target_weakness'][:80]}...")

    # Test individual attacks
    print("\n" + "-" * 80)
    print("Testing individual attacks...")
    print("-" * 80)

    attack_cases = human_attacks.generate_cases()
    attack_predictions = [doctor.predict(c.prompt) for c in attack_cases]

    print(f"\n{'Attack':<35} {'Expected':<12} {'Got':<12} {'Status':<8}")
    print("-" * 70)

    success_count = 0
    for case, pred in zip(attack_cases, attack_predictions):
        matched = pred["label"] == case.ground_truth
        status = "✓ PASS" if matched else "✗ FAIL"
        if matched:
            success_count += 1

        print(f"{case.metadata['attack_name']:<35} {case.ground_truth:<12} {pred['label']:<12} {status:<8}")

    print(f"\nAttack success rate: {success_count}/{len(attack_cases)} = {success_count/len(attack_cases):.2%}")

    # =========================================================================
    # 2. Mixed Batch Tests
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 2: MIXED BATCH TESTS")
    print("=" * 80)

    # Test 1: 50/50 mix
    print("\n[2.1] Testing 50/50 internal/external mix...")
    mixed_50 = runner.run_mixed_test(
        internal_ratio=0.5,
        total_cases=60,
        noise_levels=[0.0, 0.3, 0.6],
    )

    print(f"\nResults:")
    print(f"  Accuracy: {mixed_50.metrics.accuracy:.2%}")
    print(f"  Robustness: {mixed_50.metrics.robustness_score:.2%}")
    print(f"  Failure diversity: {mixed_50.metrics.failure_diversity:.2%}")
    print(f"\nDegradation curve:")
    for level, acc in sorted(mixed_50.metrics.degradation_curve.items()):
        print(f"  Noise {level}: {acc:.2%}")

    # Test 2: 80/20 mix (mostly internal)
    print("\n[2.2] Testing 80/20 internal/external mix...")
    mixed_80 = runner.run_mixed_test(
        internal_ratio=0.8,
        total_cases=50,
        noise_levels=[0.0, 0.3, 0.6],
    )

    print(f"\nResults:")
    print(f"  Accuracy: {mixed_80.metrics.accuracy:.2%}")
    print(f"  Robustness: {mixed_80.metrics.robustness_score:.2%}")

    # Test 3: 20/80 mix (mostly external)
    print("\n[2.3] Testing 20/80 internal/external mix...")
    mixed_20 = runner.run_mixed_test(
        internal_ratio=0.2,
        total_cases=50,
        noise_levels=[0.0, 0.3, 0.6],
    )

    print(f"\nResults:")
    print(f"  Accuracy: {mixed_20.metrics.accuracy:.2%}")
    print(f"  Robustness: {mixed_20.metrics.robustness_score:.2%}")

    # =========================================================================
    # 3. Distribution Shift Analysis
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 3: DISTRIBUTION SHIFT ANALYSIS")
    print("=" * 80)

    print("\nTesting performance as distribution shifts from internal to external...")
    shift_results = runner.run_distribution_shift_test(
        total_cases=40,
        internal_ratios=[1.0, 0.75, 0.5, 0.25, 0.0],
        noise_level=0.0,
    )

    print(f"\n{'Internal Ratio':<18} {'Accuracy':<12} {'Failures':<12}")
    print("-" * 45)

    for ratio, metrics in sorted(shift_results.items(), key=lambda x: float(x[0]) if x[0] != "distribution_shift_analysis" else 999):
        if ratio == "distribution_shift_analysis":
            continue
        print(f"{float(ratio):>15.0%} | {metrics['accuracy']:>10.2%} | {metrics['failed_cases']:>10}")

    if "distribution_shift_analysis" in shift_results:
        analysis = shift_results["distribution_shift_analysis"]
        print(f"\nDistribution Shift Analysis:")
        print(f"  Pure internal accuracy: {analysis['pure_internal_accuracy']:.2%}")
        print(f"  Pure external accuracy: {analysis['pure_external_accuracy']:.2%}")
        print(f"  Accuracy drop: {analysis['accuracy_drop']:.2%}")
        print(f"  Shift severity: {analysis['shift_severity'].upper()}")

    # =========================================================================
    # 4. Source Comparison Test
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 4: SOURCE COMPARISON TEST")
    print("=" * 80)

    print("\nComparing Doctor performance across different sources...")
    source_results = runner.run_source_comparison_test(
        cases_per_source=20,
        noise_level=0.0,
    )

    print(f"\n{'Source':<25} {'Accuracy':<12} {'Failures':<12} {'Overconfidence':<15}")
    print("-" * 65)

    for source, metrics in source_results.items():
        print(
            f"{source:<25} | {metrics['accuracy']:>10.2%} | "
            f"{metrics['failed_cases']:>10} | {metrics['overconfidence_rate']:>13.2%}"
        )

    # =========================================================================
    # 5. Noise Sensitivity Test (Enhanced)
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 5: ENHANCED NOISE SENSITIVITY TEST")
    print("=" * 80)

    noise_layer = NoiseInjectionLayer(seed=42)
    real_injector = RealWorldDataInjector(seed=42)

    # Test with real-world cases
    test_cases = real_injector.generate_cases(15)

    print(f"\nTesting noise sensitivity with {len(test_cases)} real-world cases...")
    print(f"\n{'Noise Level':<15} {'Accuracy':<12} {'Noise Types Applied':<30}")
    print("-" * 60)

    noise_results = {}
    for noise_level in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        noised_cases = [noise_layer.apply_noise(c, noise_level) for c in test_cases]
        predictions = [doctor.predict(c.prompt) for c in noised_cases]
        correct = sum(1 for c, p in zip(noised_cases, predictions) if p["label"] == c.ground_truth)
        acc = correct / len(test_cases)
        noise_results[noise_level] = acc

        # Count noise types applied
        noise_types = set()
        for case in noised_cases:
            if case.metadata.get("applied_noises"):
                noise_types.update(case.metadata["applied_noises"])

        print(f"{noise_level:>12.1%} | {acc:>10.2%} | {', '.join(sorted(noise_types))[:28]}")

    # Calculate degradation rate
    if 0.0 in noise_results and 1.0 in noise_results:
        degradation_rate = (noise_results[0.0] - noise_results[1.0]) / 1.0
        print(f"\nDegradation rate (0% → 100% noise): {degradation_rate:.2%}")

    # =========================================================================
    # 6. Failure Pattern Analysis
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 6: FAILURE PATTERN ANALYSIS")
    print("=" * 80)

    # Collect all failures from mixed test
    print("\nAnalyzing failure patterns from 50/50 mixed test...")

    failure_patterns = mixed_50.metrics.failure_patterns
    if failure_patterns:
        print(f"\n{'Pattern':<40} {'Count':<8} {'Percentage':<12}")
        print("-" * 60)

        total_failures = sum(failure_patterns.values())
        for pattern, count in sorted(failure_patterns.items(), key=lambda x: -x[1])[:10]:
            pct = count / total_failures if total_failures > 0 else 0
            print(f"{pattern:<40} | {count:>6} | {pct:>10.2%}")

        print(f"\nTotal failures: {total_failures}")
        print(f"Unique failure patterns: {len(failure_patterns)}")

    # By stress kind breakdown
    if mixed_50.metrics.by_stress_kind:
        print(f"\n{'Stress Kind':<25} {'Accuracy':<12} {'Correct':<10} {'Total':<8}")
        print("-" * 55)

        for kind, metrics in sorted(mixed_50.metrics.by_stress_kind.items()):
            if isinstance(metrics, dict):
                acc = metrics.get("accuracy", 0)
                correct = metrics.get("correct", 0)
                total = metrics.get("total", 0)
                print(f"{kind:<25} | {acc:>10.2%} | {correct:>8} | {total:>6}")

    # =========================================================================
    # 7. Recommendations
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 7: RECOMMENDATIONS")
    print("=" * 80)

    recommendations = []

    # Check overall accuracy
    if mixed_50.metrics.accuracy < 0.5:
        recommendations.append(
            "⚠ CRITICAL: Doctor accuracy below 50% on mixed stress tests\n"
            "  → Doctor is failing more than half of external cases\n"
            "  → Immediate intervention required before real-world deployment"
        )
    elif mixed_50.metrics.accuracy < 0.7:
        recommendations.append(
            "⚠ WARNING: Doctor accuracy below 70% on mixed stress tests\n"
            "  → Doctor struggles with real-world ambiguity\n"
            "  → Focus on improving reasoning for edge cases"
        )

    # Check robustness
    if mixed_50.metrics.robustness_score < 0.8:
        recommendations.append(
            "⚠ WARNING: Doctor degrades significantly under noise\n"
            f"  → Robustness score: {mixed_50.metrics.robustness_score:.2%}\n"
            "  → Add noise augmentation to evaluation pipeline\n"
            "  → Implement input validation and cleaning"
        )

    # Check failure diversity
    if mixed_50.metrics.failure_diversity < 0.4:
        recommendations.append(
            "⚠ WARNING: Failures are concentrated in few patterns\n"
            f"  → Failure diversity: {mixed_50.metrics.failure_diversity:.2%}\n"
            "  → Doctor has specific blind spots that can be systematically exploited\n"
            "  → Address top failure patterns individually"
        )

    # Check specific failure patterns
    if "undercommitted_correct" in failure_patterns and failure_patterns["undercommitted_correct"] > 10:
        recommendations.append(
            "⚠ ISSUE: High rate of 'undercommitted_correct' failures\n"
            f"  → Count: {failure_patterns['undercommitted_correct']}\n"
            "  → Doctor is classifying correct responses as 'partial'\n"
            "  → Review fallback behavior in decision engine\n"
            "  → Consider adjusting thresholds or adding new rules"
        )

    if "missed_undefined" in failure_patterns and failure_patterns["missed_undefined"] > 10:
        recommendations.append(
            "⚠ ISSUE: High rate of 'missed_undefined' failures\n"
            f"  → Count: {failure_patterns['missed_undefined']}\n"
            "  → Doctor is not recognizing implicit ambiguity\n"
            "  → Expand evidence extraction to detect implicit undefined cases\n"
            "  → Add rules for detecting contradictions not explicitly stated"
        )

    if not recommendations:
        recommendations.append("✓ No critical issues detected")

    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec}")

    # =========================================================================
    # Final Summary
    # =========================================================================
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    print(f"\n✓ Stress dashboard completed successfully")
    print(f"✓ Test configuration:")
    print(f"  - Seed: 42")
    print(f"  - Mixed test cases: {mixed_50.metrics.total_cases}")
    print(f"  - Internal/External ratio: 50/50")
    print(f"  - Noise levels tested: [0.0, 0.3, 0.6]")
    print(f"  - Human attacks tested: {len(attack_cases)}")

    print(f"\n✓ Key metrics:")
    print(f"  - Overall accuracy: {mixed_50.metrics.accuracy:.2%}")
    print(f"  - Robustness under noise: {mixed_50.metrics.robustness_score:.2%}")
    print(f"  - Failure diversity: {mixed_50.metrics.failure_diversity:.2%}")
    print(f"  - Human attack success rate: {success_count}/{len(attack_cases)} = {success_count/len(attack_cases):.2%}")

    print("\n✓ Complete!")


if __name__ == "__main__":
    main()
