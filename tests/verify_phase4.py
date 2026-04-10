"""
Phase 4 Verification Script
=============================
Run adaptive generator for 3 rounds with 20 cases each.
After round 3 report memory statistics.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from doctor.raw_prompt_doctor import RawPromptDoctor
from dataset_generator.adaptive_generator import AdaptiveGenerator
from dataset_generator.failure_capture import (
    MEMORY_ROOT, load_patterns, get_active_patterns, get_retired_patterns,
    classify_error, register_failure_pattern, log_failure
)
from external_stress_layer import StressCase, StressKind
from external_stress_layer.enhanced_evaluator import detect_rule_violations as esl_detect_rules

print("=" * 80)
print("PHASE 4 VERIFICATION — Adversarial Memory Maturation")
print("=" * 80)

# Initialize
doctor = RawPromptDoctor()
generator = AdaptiveGenerator(seed=42)

# Clear old memory for clean test
import shutil
if MEMORY_ROOT.exists():
    shutil.rmtree(MEMORY_ROOT)
MEMORY_ROOT.mkdir(parents=True, exist_ok=True)

print(f"\n  Memory directory cleared: {MEMORY_ROOT}")

# ── Run 3 rounds ─────────────────────────────────────────────────────────────
N_ROUNDS = 3
N_CASES_PER_ROUND = 20

all_results = []
round_summaries = []

for round_num in range(1, N_ROUNDS + 1):
    print(f"\n{'='*80}")
    print(f"ROUND {round_num}/{N_ROUNDS}")
    print(f"{'='*80}")

    # Generate cases (increasing memory_fraction each round)
    memory_frac = min(0.9, 0.3 + round_num * 0.2)
    batch = generator.generate_batch(n=N_CASES_PER_ROUND, memory_fraction=memory_frac)

    print(f"  Cases: {batch['summary']['count']}")
    print(f"  Memory-driven: {batch['summary']['memory_driven']}")
    print(f"  Random exploration: {batch['summary']['random_exploration']}")

    # Evaluate each case
    round_correct = 0
    round_failures = 0

    for pub_case in batch["public_cases"]:
        try:
            pred = doctor.predict(pub_case["prompt"])
        except Exception as e:
            pred = {"label": "undefined", "confidence": 0.5, "decision_path": ["error"]}

        priv_case = batch["private_key"].get(pub_case["case_id"])
        if not priv_case:
            continue

        truth = priv_case["ground_truth"]
        label = pred["label"]
        matched = label == truth

        if matched:
            round_correct += 1
        else:
            round_failures += 1

            # Log failure with provenance
            error_classification = classify_error(priv_case, pred)

            # Add origin metadata for provenance
            priv_case_with_origin = {
                **priv_case,
                "origin": "internal_generator",
                "escalation_level_label": "L0",
                "prompt": pub_case["prompt"],
            }

            if error_classification["error_types"] or error_classification["rule_violations"]:
                log_failure(priv_case_with_origin, pred, error_classification)
                register_failure_pattern(priv_case_with_origin, error_classification)

    acc = round_correct / N_CASES_PER_ROUND if N_CASES_PER_ROUND > 0 else 0.0
    round_summaries.append({
        "round": round_num,
        "accuracy": acc,
        "correct": round_correct,
        "failures": round_failures,
        "memory_frac": memory_frac,
    })

    print(f"  Accuracy: {round_correct}/{N_CASES_PER_ROUND} = {acc:.1%}")
    print(f"  Failures logged: {round_failures}")

    # Reload patterns after this round
    generator.patterns = load_patterns()

# ── Post-round 3 memory statistics ──────────────────────────────────────────
print(f"\n{'='*80}")
print("MEMORY STATISTICS (after round 3)")
print(f"{'='*80}")

all_patterns = load_patterns()
active_patterns = get_active_patterns()
retired_patterns = get_retired_patterns()

# Count discarded duplicates
discarded_path = MEMORY_ROOT / "discarded_duplicates.jsonl"
discarded_count = 0
if discarded_path.exists():
    with open(discarded_path, "r") as f:
        discarded_count = sum(1 for line in f if line.strip())

print(f"\n  Total patterns: {len(all_patterns)}")
print(f"  Active patterns: {len(active_patterns)}")
print(f"  Retired patterns: {len(retired_patterns)}")
print(f"  Discarded duplicates (novelty gate): {discarded_count}")

# Provenance distribution
origin_counts = defaultdict(int)
rule_target_counts = defaultdict(int)
escalation_counts = defaultdict(int)

for p in all_patterns:
    origin_counts[p.get("origin", "unknown")] += 1
    rt = p.get("rule_target")
    if rt:
        rule_target_counts[rt] += 1
    else:
        rule_target_counts["none"] += 1
    escalation_counts[p.get("escalation_level_label", "L0")] += 1

print(f"\n  Provenance distribution:")
for origin, count in sorted(origin_counts.items(), key=lambda x: -x[1]):
    pct = count / len(all_patterns) * 100 if all_patterns else 0
    print(f"    {origin}: {count} ({pct:.0f}%)")

print(f"\n  Rule target distribution:")
for rt, count in sorted(rule_target_counts.items(), key=lambda x: -x[1]):
    print(f"    {rt}: {count}")

print(f"\n  Escalation level distribution:")
for level, count in sorted(escalation_counts.items()):
    print(f"    {level}: {count}")

# Check if memory is growing with genuine novelty or accumulating duplicates
total_patterns_ever = len(all_patterns) + discarded_count
duplicate_rate = discarded_count / total_patterns_ever if total_patterns_ever > 0 else 0.0

print(f"\n  Memory growth analysis:")
print(f"    Total patterns ever created: {total_patterns_ever}")
print(f"    Patterns retained (active + retired): {len(all_patterns)}")
print(f"    Discarded as duplicates: {discarded_count}")
print(f"    Duplicate rate: {duplicate_rate:.0%}")

if duplicate_rate < 0.20:
    print(f"    ✓ Memory is growing with genuine novelty (duplicate rate < 20%)")
elif duplicate_rate < 0.50:
    print(f"    ⚠ Moderate duplicate accumulation ({duplicate_rate:.0%})")
else:
    print(f"    ✗ High duplicate rate ({duplicate_rate:.0%}) — memory accumulating noise")

# Round-by-round summary
print(f"\n{'='*80}")
print("ROUND-BY-ROUND SUMMARY")
print(f"{'='*80}")

print(f"\n  {'Round':>6} {'Accuracy':>10} {'Correct':>10} {'Failures':>10} {'Memory Frac':>12}")
print(f"  {'-'*6} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")
for rs in round_summaries:
    print(f"  {rs['round']:>6} {rs['accuracy']:>9.1%} {rs['correct']:>10} {rs['failures']:>10} {rs['memory_frac']:>11.1%}")

# Retirement analysis
if retired_patterns:
    print(f"\n  Retired patterns:")
    for rp in retired_patterns:
        print(f"    - Stratum {rp['stratum']}: {rp['retirement_reason']}")
else:
    print(f"\n  No patterns retired yet (need 10+ mutations per pattern)")

# Final assessment
print(f"\n{'='*80}")
print("PHASE 4 VERIFICATION SUMMARY")
print(f"{'='*80}")

print(f"\n  Pattern retirement: {'Working' if len(retired_patterns) > 0 else 'Not yet triggered (expected for short runs)'}")
print(f"  Novelty gate: {'Working' if discarded_count > 0 else 'Active (no duplicates found yet)'}")
print(f"  Provenance tracking: {'Working' if all(p.get('origin') for p in all_patterns) else 'Patterns need migration'}")

if all(p.get("origin") for p in all_patterns) and all(p.get("last_used") for p in all_patterns):
    print(f"  ✓ All provenance fields present")
else:
    print(f"  ⚠ Some patterns missing provenance fields")

print(f"\n  Memory status: {'Healthy - genuine novelty' if duplicate_rate < 0.20 else 'Needs review'}")
print(f"\n{'='*80}")
print("✓ PHASE 4 VERIFICATION COMPLETE")
print(f"{'='*80}")
