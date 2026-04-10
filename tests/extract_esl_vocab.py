"""Extract vocabulary from ESL cases to understand what correct/partial/undefined responses look like in real-world prompts."""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks

# Collect all ESL cases
rw = RealWorldDataInjector(seed=42)
cd = CrossDomainStressor(seed=42)
hc = HumanCraftedAttacks(seed=42)

rw_cases = rw.generate_cases(20)
cd_cases = cd.generate_cases(20)
hc_cases = hc.generate_cases()

all_cases = rw_cases + cd_cases + hc_cases

# Group by ground truth
by_gt = {}
for case in all_cases:
    gt = case.ground_truth
    if gt not in by_gt:
        by_gt[gt] = []
    by_gt[gt].append(case)

for gt, cases in sorted(by_gt.items()):
    print(f"\n{'='*80}")
    print(f"GROUND TRUTH: {gt} ({len(cases)} cases)")
    print(f"{'='*80}")
    for case in cases:
        print(f"\n--- {case.case_id} ({case.metadata.get('source_type', case.metadata.get('source_domain', case.metadata.get('attack_name', 'unknown')))}) ---")
        # Show key phrases from the proposed response
        if "PROPOSED RESPONSE" in case.prompt:
            resp_start = case.prompt.index("PROPOSED RESPONSE")
            response = case.prompt[resp_start:]
            print(f"  Response: {response[:300]}")
        else:
            print(f"  [No PROPOSED RESPONSE found]")
