"""
Phase A — Step 2: Examine prompt structure for all GT classes.
Look at the PROPOSED RESPONSE sections for correct, partial, and incorrect cases.
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
from dataset_generator.adaptive_generator import AdaptiveGenerator

gen = AdaptiveGenerator(seed=42)
internal_batch = gen.generate_batch(n=30, memory_fraction=0.5)
cases = []
for pub in internal_batch["public_cases"]:
    priv = internal_batch["private_key"].get(pub["case_id"])
    if priv:
        cases.append(StressCase(
            case_id=pub["case_id"], prompt=pub["prompt"],
            stress_kind=StressKind.MIXED, ground_truth=priv["ground_truth"],
        ))

rw = RealWorldDataInjector(seed=42)
cd = CrossDomainStressor(seed=42)
hc = HumanCraftedAttacks(seed=42)
esl_cases = rw.generate_cases(15) + cd.generate_cases(15) + hc.generate_cases()
cases.extend(esl_cases)

for gt in ["correct", "partial", "incorrect"]:
    gt_cases = [c for c in cases if c.ground_truth == gt][:3]
    print(f"\n{'='*80}")
    print(f"GT = {gt.upper()} ({len(gt_cases)} examples)")
    print(f"{'='*80}")
    for case in gt_cases:
        print(f"\n--- {case.case_id} ({len(case.prompt)} chars) ---")
        # Find PROPOSED RESPONSE section
        idx = case.prompt.find("PROPOSED RESPONSE")
        if idx >= 0:
            print(f"  PROPOSED RESPONSE: {case.prompt[idx:idx+200]}")
        else:
            # Show the last 200 chars
            print(f"  (no PROPOSED RESPONSE found)")
            print(f"  Last 200: ...{case.prompt[-200:]}")
        print()
