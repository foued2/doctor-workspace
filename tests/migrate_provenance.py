"""
Migration Script — Phase 4: Provenance Backfill
=================================================
One-time migration that adds provenance fields to all existing patterns
in adversarial_memory/patterns.json.

Provenance fields added:
- origin: "ESL" for ESL cases, "internal_generator" for generator cases
- rule_target: derived from rule_violations or error_types
- escalation_level_label: "L0" for existing patterns
- last_used: current timestamp
- mutation_count: 0 for existing patterns
- retired: false
- retirement_reason: null
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from pathlib import Path
from datetime import datetime, timezone
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataset_generator.failure_capture import MEMORY_ROOT, load_patterns, save_patterns, _pattern_hash

def migrate():
    patterns_path = MEMORY_ROOT / "patterns.json"

    if not patterns_path.exists():
        print("No patterns.json found — nothing to migrate.")
        return

    patterns = load_patterns()
    print(f"Found {len(patterns)} existing patterns.")

    migrated_count = 0
    now = datetime.now(timezone.utc).isoformat()

    for p in patterns:
        # Skip if already has provenance fields
        if "origin" in p and "last_used" in p:
            migrated_count += 1
            continue

        # Determine origin from stratum/error pattern
        stratum = p.get("stratum", "")
        error_types = p.get("error_types", [])

        # Heuristic: ESL cases came from real-world evaluation runs
        # Generator cases came from internal adversarial generation
        # Since existing patterns are from the verification runs, mark as ESL
        p["origin"] = "ESL"

        # Derive rule_target if not present
        if "rule_target" not in p:
            rule_violations = p.get("rule_violations", [])
            if rule_violations:
                p["rule_target"] = max(rule_violations, key=lambda r: {"R2": 3.0, "R3": 2.0, "R1": 1.0}.get(r, 0.0))
            elif "failed_undefined_detection" in error_types:
                p["rule_target"] = "R3"
            elif "missed_contradiction" in error_types:
                p["rule_target"] = "R1"
            elif "trusted_corrupted_label" in error_types:
                p["rule_target"] = "R2"
            else:
                p["rule_target"] = None

        # Add escalation level label
        if "escalation_level_label" not in p:
            esc_level = p.get("escalation_level", 0)
            if esc_level == 0:
                p["escalation_level_label"] = "L0"
            elif esc_level == 1:
                p["escalation_level_label"] = "L1"
            elif esc_level == 2:
                p["escalation_level_label"] = "L2"
            else:
                p["escalation_level_label"] = "L3"

        # Add missing provenance fields
        if "mutation_count" not in p:
            p["mutation_count"] = 0
        if "last_used" not in p:
            p["last_used"] = now
        if "retired" not in p:
            p["retired"] = False
        if "retirement_reason" not in p:
            p["retirement_reason"] = None
        if "is_ambiguous" not in p:
            p["is_ambiguous"] = False
        if "prompt_text" not in p:
            p["prompt_text"] = ""

        migrated_count += 1

    save_patterns(patterns)

    print(f"Migration complete: {migrated_count} patterns updated.")

    # Show provenance distribution
    origin_counts = {}
    rule_target_counts = {}
    for p in patterns:
        origin = p.get("origin", "unknown")
        origin_counts[origin] = origin_counts.get(origin, 0) + 1

        rt = p.get("rule_target")
        if rt:
            rule_target_counts[rt] = rule_target_counts.get(rt, 0) + 1
        else:
            rule_target_counts["none"] = rule_target_counts.get("none", 0) + 1

    print(f"\nProvenance distribution:")
    for origin, count in sorted(origin_counts.items(), key=lambda x: -x[1]):
        pct = count / len(patterns) * 100
        print(f"  {origin}: {count} ({pct:.0f}%)")

    print(f"\nRule target distribution:")
    for rt, count in sorted(rule_target_counts.items(), key=lambda x: -x[1]):
        print(f"  {rt}: {count}")

if __name__ == "__main__":
    migrate()
