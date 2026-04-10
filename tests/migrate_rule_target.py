"""
Migration Script — Phase 3: Rule Target Backfill
==================================================
One-time migration that adds `rule_target` field to all existing entries
in adversarial_memory/failures.jsonl.

Derives rule_target from rule_violations list:
- If multiple violations exist, the highest-weight rule becomes the target
- Weight order: R2 (3.0) > R3 (2.0) > R1 (1.0)
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataset_generator.failure_capture import MEMORY_ROOT

RULE_WEIGHTS = {"R2": 3.0, "R3": 2.0, "R1": 1.0}

def migrate():
    failures_path = MEMORY_ROOT / "failures.jsonl"
    
    if not failures_path.exists():
        print("No failures.jsonl found — nothing to migrate.")
        return
    
    # Read all existing records
    records = []
    with open(failures_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    
    print(f"Found {len(records)} existing failure records.")
    
    migrated_count = 0
    skipped_count = 0
    
    for record in records:
        # Skip if already has rule_target
        if "rule_target" in record:
            skipped_count += 1
            continue
        
        # Derive rule_target from rule_violations
        rule_violations = record.get("rule_violations", [])
        
        if rule_violations:
            # Pick highest-weight rule as target
            rule_target = max(rule_violations, key=lambda r: RULE_WEIGHTS.get(r, 0.0))
        else:
            # No rule violations — derive from error_types heuristically
            error_types = record.get("error_types", [])
            if "failed_undefined_detection" in error_types:
                rule_target = "R3"  # false confidence
            elif "missed_contradiction" in error_types:
                rule_target = "R1"  # contradiction blindness
            elif "trusted_corrupted_label" in error_types:
                rule_target = "R2"  # corruption trust
            else:
                rule_target = None  # No rule target applicable
        
        record["rule_target"] = rule_target
        migrated_count += 1
    
    # Write back
    with open(failures_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    print(f"Migration complete:")
    print(f"  Migrated: {migrated_count}")
    print(f"  Skipped (already had rule_target): {skipped_count}")
    
    # Show distribution
    target_counts = {}
    for record in records:
        target = record.get("rule_target")
        if target:
            target_counts[target] = target_counts.get(target, 0) + 1
        else:
            target_counts["none"] = target_counts.get("none", 0) + 1
    
    print(f"\nRule target distribution:")
    for target, count in sorted(target_counts.items(), key=lambda x: -x[1]):
        print(f"  {target}: {count}")

if __name__ == "__main__":
    migrate()
