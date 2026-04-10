"""Investigate the 8 undefined cases that Layer 0.5 missed."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doctor.undefined_detection import classify_undefined, detect_undefined, undefined_score
from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
from dataset_generator.adaptive_generator import AdaptiveGenerator

# Rebuild the same batch as verify_production.py
gen = AdaptiveGenerator(seed=42)
internal_batch = gen.generate_batch(n=30, memory_fraction=0.5)
cases = []
for pub in internal_batch["public_cases"]:
    priv = internal_batch["private_key"].get(pub["case_id"])
    if priv:
        cases.append(StressCase(
            case_id=pub["case_id"], prompt=pub["prompt"],
            stress_kind=StressKind.MIXED, ground_truth=priv["ground_truth"],
            metadata={"contradiction": priv.get("contradiction", False)},
        ))

rw = RealWorldDataInjector(seed=42)
cd = CrossDomainStressor(seed=42)
hc = HumanCraftedAttacks(seed=42)
esl_cases = rw.generate_cases(15) + cd.generate_cases(15) + hc.generate_cases()
cases.extend(esl_cases)

# Find undefined GT cases
undefined_cases = [c for c in cases if c.ground_truth == "undefined"]
print(f"Total undefined GT cases: {len(undefined_cases)}\n")

for case in undefined_cases:
    r = classify_undefined(case.prompt)
    status = "✓ DETECTED" if r.is_undefined else "✗ MISSED"
    print(f"{'='*70}")
    print(f"{status} | {case.case_id} | score={r.score:.3f} | signals={len(r.signals)}")
    print(f"  Categories: {list(r.category_scores.keys())}")
    print(f"  Scores: {r.category_scores}")
    if r.signals:
        for s in r.signals:
            print(f"    [{s.category}] strength={s.strength} matched='{s.matched_text}'")
    else:
        print(f"    (no signals matched)")
    # Show the full prompt for missed cases
    if not r.is_undefined:
        print(f"\n  FULL PROMPT:")
        print(f"  {case.prompt[:500]}")
        if len(case.prompt) > 500:
            print(f"  ... ({len(case.prompt)} chars total)")
    print()
