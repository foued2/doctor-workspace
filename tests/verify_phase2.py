"""
Phase 2 Verification Script
============================
Run ESL experiment and show:
1. 5 sample failure log entries with rule_violations field
2. Rule violation distribution across ESL cases
3. Confirm R3 is the dominant violation type given current undefined recall gap
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from doctor.raw_prompt_doctor import RawPromptDoctor
from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator, detect_rule_violations
from dataset_generator.failure_capture import (
    classify_error, log_failure, MEMORY_ROOT, RULE_WEIGHT_MULTIPLIERS
)

def generate_esl_cases(n: int = 60, seed: int = 42):
    """Generate external stress layer cases."""
    cases = []
    rw = RealWorldDataInjector(seed=seed)
    cd = CrossDomainStressor(seed=seed)
    hc = HumanCraftedAttacks(seed=seed)
    cases.extend(rw.generate_cases(n // 3))
    cases.extend(cd.generate_cases(n // 3))
    cases.extend(hc.generate_cases())
    return cases

print("=" * 80)
print("PHASE 2 VERIFICATION — Rule Attribution Layer")
print("=" * 80)

# Generate ESL cases
print("\n[1/4] Generating ESL cases...")
doctor = RawPromptDoctor()
cases = generate_esl_cases(n=60, seed=42)
print(f"  ✓ {len(cases)} ESL cases generated")

# Run predictions
print("\n[2/4] Running Doctor predictions...")
predictions = []
for i, case in enumerate(cases):
    try:
        pred = doctor.predict(case.prompt)
        predictions.append(pred)
    except Exception as e:
        predictions.append({
            "case_id": case.case_id,
            "label": "undefined",
            "confidence": 0.5,
            "decision_path": ["error"],
            "error": str(e),
        })
    if (i + 1) % 20 == 0:
        print(f"  Processed {i + 1}/{len(cases)} cases...", end='\r')
print(f"\n  ✓ Completed")

# Run evaluation with rule violation detection
print("\n[3/4] Evaluating with rule violation detection...")
evaluator = EnhancedEvaluator()
metrics = evaluator.evaluate_batch(cases, predictions)

print(f"\n  Overall accuracy: {metrics.accuracy:.2%}")
print(f"  Failed cases: {metrics.failed_cases}")
print(f"\n  Rule Violation Distribution:")
for rule, count in sorted(metrics.rule_violations.items(), key=lambda x: -x[1]):
    pct = count / metrics.failed_cases if metrics.failed_cases > 0 else 0.0
    print(f"    {rule}: {count} ({pct:.0%} of failures)")

print(f"\n  Weighted rule violation rate: {metrics.rule_violation_rate:.4f}")

# Show sample failure log entries
print("\n[4/4] Generating failure logs...")

# Clear old failures
MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
failures_path = MEMORY_ROOT / "failures.jsonl"
if failures_path.exists():
    failures_path.unlink()

# Log failures with new schema
failure_records = []
for case, pred in zip(cases, predictions):
    if pred["label"] != case.ground_truth:
        error_classification = classify_error({
            "case_id": case.case_id,
            "stratum": case.metadata.get("stratum", "A"),
            "ground_truth": case.ground_truth,
            "prompt": case.prompt,
            "contradiction": case.metadata.get("contradiction", False),
            "corrupted_label": case.metadata.get("corrupted_label", False),
            "signal_inversion": case.metadata.get("signal_inversion", False),
        }, pred)
        
        if error_classification["error_types"] or error_classification["rule_violations"]:
            record = log_failure({
                "case_id": case.case_id,
                "stratum": case.metadata.get("stratum", "A"),
                "ground_truth": case.ground_truth,
                "prompt": case.prompt,
                "contradiction": case.metadata.get("contradiction", False),
                "corrupted_label": case.metadata.get("corrupted_label", False),
                "signal_inversion": case.metadata.get("signal_inversion", False),
            }, pred, error_classification)
            failure_records.append(record)

print(f"  ✓ {len(failure_records)} failure records logged to failures.jsonl")

# Show 5 sample entries
print("\n" + "=" * 80)
print("SAMPLE FAILURE LOG ENTRIES (first 5)")
print("=" * 80)

for i, record in enumerate(failure_records[:5]):
    print(f"\n--- Entry {i+1} ---")
    print(f"  case_id: {record['case_id']}")
    print(f"  stratum: {record['stratum']}")
    print(f"  ground_truth: {record['ground_truth']}")
    print(f"  doctor_label: {record['doctor_label']}")
    print(f"  doctor_confidence: {record['doctor_confidence']}")
    print(f"  error_types: {record['error_types']}")
    print(f"  rule_violations: {record['rule_violations']}")  # PHASE 2: New field
    print(f"  features: {record['features']}")

# Rule violation summary
print("\n" + "=" * 80)
print("RULE VIOLATION DISTRIBUTION")
print("=" * 80)

rule_counts = {}
for record in failure_records:
    for rule in record.get("rule_violations", []):
        rule_counts[rule] = rule_counts.get(rule, 0) + 1

total_violations = sum(rule_counts.values())
print(f"\n  Total rule violations detected: {total_violations}")
print(f"  Total failure records: {len(failure_records)}")

for rule in ["R1", "R2", "R3"]:
    count = rule_counts.get(rule, 0)
    pct = count / total_violations if total_violations > 0 else 0.0
    weight = RULE_WEIGHT_MULTIPLIERS[rule]
    print(f"  {rule}: {count:>3} ({pct:.0%} of violations) [weight: {weight}x]")

# Confirm dominant violation type
if rule_counts:
    dominant = max(rule_counts, key=rule_counts.get)
    print(f"\n  Dominant violation type: {dominant} ({rule_counts[dominant]} occurrences)")
    if dominant == "R3":
        print(f"  ✓ CONFIRMED: R3 (false confidence) is dominant, as expected given undefined recall gap")
    else:
        print(f"  ⚠ Expected R3 to be dominant, but {dominant} has most violations")

print("\n" + "=" * 80)
print("✓ PHASE 2 VERIFICATION COMPLETE")
print("=" * 80)
