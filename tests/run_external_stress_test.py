"""
External Stress Layer - Example Script
=======================================
Demonstrates how to use the ESL to stress test the Doctor outside the synthetic cage.

This script runs:
1. Comprehensive stress test with all sources
2. Degradation curve analysis
3. Recovery test
4. Attack catalog display

Usage:
    python tests/run_external_stress_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from doctor.raw_prompt_doctor import RawPromptDoctor
from external_stress_layer import (
    StressTestOrchestrator,
    RealWorldInjector,
    NoiseInjectionLayer,
    CrossDomainStressor,
    HumanCraftedAttacks,
)


def main():
    print("=" * 80)
    print("EXTERNAL STRESS TEST - BREAKING THE DOCTOR OUT OF THE CAGE")
    print("=" * 80)
    
    # Initialize Doctor
    doctor = RawPromptDoctor()
    
    # Initialize orchestrator
    orchestrator = StressTestOrchestrator(doctor=doctor, seed=42)
    
    # =========================================================================
    # 1. Display attack catalog
    # =========================================================================
    print("\n" + "=" * 80)
    print("HUMAN-CRAFTED ATTACK CATALOG")
    print("=" * 80)
    
    attacks = orchestrator.get_attack_catalog()
    for i, attack in enumerate(attacks, 1):
        print(f"\n{i}. {attack['name']}")
        print(f"   Description: {attack['description']}")
        print(f"   Target: {attack['target_weakness']}")
        print(f"   Expected failure: {attack['expected_failure']}")
    
    # =========================================================================
    # 2. Run comprehensive stress test
    # =========================================================================
    print("\n" + "=" * 80)
    print("COMPREHENSIVE STRESS TEST")
    print("=" * 80)
    
    results = orchestrator.run_stress_test(
        n_external=30,  # Cases per external source
        noise_levels=[0.0, 0.3, 0.6],  # Test at 3 noise levels
        include_generator=True,
        include_real_world=True,
        include_cross_domain=True,
        include_human_attacks=True,
    )
    
    print("\n" + results.summary())
    
    # =========================================================================
    # 3. Degradation curve analysis
    # =========================================================================
    print("\n" + "=" * 80)
    print("DEGRADATION CURVE ANALYSIS")
    print("=" * 80)
    
    degradation = orchestrator.run_degradation_analysis(
        noise_levels=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
    )
    
    print(f"\nDegradation Curve:")
    print(f"{'Noise Level':>12} | {'Accuracy':>10} | {'Failures':>10}")
    print("-" * 40)
    for level, metrics in sorted(degradation["curve"].items(), key=lambda x: float(x[0])):
        print(f"{float(level):>10.1%} | {metrics['accuracy']:>10.2%} | {metrics['failed_cases']:>10}")
    
    print(f"\nAUC (normalized): {degradation['auc_normalized']:.4f}")
    print(f"Initial accuracy: {degradation['initial_accuracy']:.2%}")
    print(f"Final accuracy: {degradation['final_accuracy']:.2%}")
    print(f"Degradation rate: {degradation['degradation_rate']:.4f}")
    
    # =========================================================================
    # 4. Recovery test
    # =========================================================================
    print("\n" + "=" * 80)
    print("RECOVERY TEST")
    print("=" * 80)
    
    recovery = orchestrator.run_recovery_test()
    
    print(f"\nInitial failures: {recovery['initial_failures']}")
    print(f"Recovered: {recovery.get('recovered', 0)}")
    print(f"Recovery rate: {recovery['recovery_rate']:.2%}")
    print(f"Still failing: {recovery.get('still_failing', 0)}")
    
    # =========================================================================
    # 5. Individual component tests
    # =========================================================================
    print("\n" + "=" * 80)
    print("INDIVIDUAL COMPONENT TESTS")
    print("=" * 80)
    
    # Real-world only
    print("\n[Real-World Injection]")
    rw_injector = RealWorldInjector(seed=42)
    rw_cases = rw_injector.generate_cases(10)
    rw_predictions = [doctor.predict(c.prompt) for c in rw_cases]
    rw_correct = sum(1 for c, p in zip(rw_cases, rw_predictions) if p["label"] == c.ground_truth)
    print(f"  Accuracy: {rw_correct}/{len(rw_cases)} = {rw_correct/len(rw_cases):.2%}")
    
    # Cross-domain only
    print("\n[Cross-Domain Stress]")
    cd_stressor = CrossDomainStressor(seed=42)
    cd_cases = cd_stressor.generate_cases(10)
    cd_predictions = [doctor.predict(c.prompt) for c in cd_cases]
    cd_correct = sum(1 for c, p in zip(cd_cases, cd_predictions) if p["label"] == c.ground_truth)
    print(f"  Accuracy: {cd_correct}/{len(cd_cases)} = {cd_correct/len(cd_cases):.2%}")
    
    # Human attacks only
    print("\n[Human-Crafted Attacks]")
    h_attacks = HumanCraftedAttacks(seed=42)
    h_cases = h_attacks.generate_cases()
    h_predictions = [doctor.predict(c.prompt) for c in h_cases]
    h_correct = sum(1 for c, p in zip(h_cases, h_predictions) if p["label"] == c.ground_truth)
    print(f"  Accuracy: {h_correct}/{len(h_cases)} = {h_correct/len(h_cases):.2%}")
    
    # Show which attacks succeeded/failed
    print("\n  Attack results:")
    for case, pred in zip(h_cases, h_predictions):
        status = "✓" if pred["label"] == case.ground_truth else "✗"
        print(f"    {status} {case.metadata['attack_name']}: expected={case.ground_truth}, got={pred['label']}")
    
    # =========================================================================
    # 6. Noise sensitivity test
    # =========================================================================
    print("\n" + "=" * 80)
    print("NOISE SENSITIVITY TEST")
    print("=" * 80)
    
    noise_layer = NoiseInjectionLayer(seed=42)
    test_cases = rw_injector.generate_cases(5)
    
    print(f"\n{'Noise Level':>12} | {'Accuracy':>10}")
    print("-" * 30)
    for noise_level in [0.0, 0.2, 0.4, 0.6, 0.8]:
        noised_cases = [noise_layer.apply_noise(c, noise_level) for c in test_cases]
        predictions = [doctor.predict(c.prompt) for c in noised_cases]
        correct = sum(1 for c, p in zip(noised_cases, predictions) if p["label"] == c.ground_truth)
        print(f"{noise_level:>10.1%} | {correct/len(test_cases):>10.2%}")
    
    # =========================================================================
    # Final summary
    # =========================================================================
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    print(f"\n✓ Stress test completed successfully")
    print(f"✓ Total cases evaluated: {results.metrics.total_cases}")
    print(f"✓ Overall accuracy: {results.metrics.accuracy:.2%}")
    print(f"✓ Robustness score: {results.metrics.robustness_score:.2%}")
    print(f"✓ Failure diversity: {results.metrics.failure_diversity:.2%}")
    
    print("\nKey insights:")
    print(f"  - The Doctor performs {'well' if results.metrics.accuracy > 0.7 else 'poorly'} on mixed stress tests")
    print(f"  - Robustness under noise is {'acceptable' if results.metrics.robustness_score > 0.8 else 'concerning'}")
    print(f"  - Failure patterns are {'diverse' if results.metrics.failure_diversity > 0.5 else 'concentrated'}")
    
    if results.metrics.failure_patterns:
        print("\nTop failure patterns:")
        sorted_patterns = sorted(results.metrics.failure_patterns.items(), key=lambda x: -x[1])
        for pattern, count in sorted_patterns[:5]:
            print(f"  - {pattern}: {count} failures")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if results.metrics.accuracy < 0.6:
        print("⚠ CRITICAL: Doctor accuracy below 60% on stress tests")
        print("  → Doctor is not ready for real-world deployment")
        print("  → Focus on improving base reasoning before adding complexity")
    
    if results.metrics.robustness_score < 0.7:
        print("⚠ WARNING: Doctor degrades significantly under noise")
        print("  → Add noise augmentation to training/evaluation pipeline")
        print("  → Implement input validation and cleaning")
    
    if results.metrics.failure_diversity < 0.4:
        print("⚠ WARNING: Failures are concentrated in few patterns")
        print("  → Doctor has specific blind spots that can be systematically exploited")
        print("  → Address top failure patterns individually")
    
    print("\n✓ Complete!")


if __name__ == "__main__":
    main()
