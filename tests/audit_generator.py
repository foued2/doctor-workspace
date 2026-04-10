"""Audit generator for ground truth alignment issues."""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataset_generator.generator import build_experiment

# Audit across multiple seeds
total_audited = 0
total_correct = 0
total_partial = 0
total_undefined = 0
mislabeled_correct = []  # GT=correct but has partial signal text
mislabeled_partial = []  # GT=partial but has correct signal text
mislabeled_undefined = []  # GT=undefined but has no undefined signal

for seed in [42, 100, 200, 300, 400]:
    exp = build_experiment(seed=seed, baseline_size=40, attack_size=80)
    all_pubs = exp['baseline']['public_cases'] + exp['attack']['public_cases']
    pk = {**exp['baseline']['private_key'], **exp['attack']['private_key']}
    
    for p in all_pubs:
        total_audited += 1
        case_id = p['case_id']
        gt = pk[case_id]['ground_truth']
        prompt_lower = p['prompt'].lower()
        
        if gt == 'correct':
            total_correct += 1
            # Check for partial signal text
            partial_signals = [
                'common path but leaves',
                'exception route unresolved',
                'picks one frontier without',
                'without proving why competing',
                'commits to a single answer even though',
            ]
            for sig in partial_signals:
                if sig in prompt_lower:
                    mislabeled_correct.append((case_id, seed, gt, sig, p['prompt'][:200]))
                    break
                    
        elif gt == 'partial':
            total_partial += 1
            # Check for correct signal text that contradicts partial label
            correct_signals = [
                'preserves legal priority',
                'reconciles late corrections',
                'keeps an audit trail',
            ]
            # Also check for undefined signals that should make it undefined not partial
            undefined_signals = [
                'prevents a single decidable target',
                'logically undecidable',
            ]
            for sig in correct_signals:
                if sig in prompt_lower:
                    mislabeled_partial.append((case_id, seed, gt, sig, p['prompt'][:200]))
                    break
            for sig in undefined_signals:
                if sig in prompt_lower:
                    mislabeled_undefined.append((case_id, seed, gt, sig, p['prompt'][:200]))
                    break
                    
        elif gt == 'undefined':
            total_undefined += 1

print("=" * 80)
print("GENERATOR GROUND TRUTH AUDIT")
print("=" * 80)
print(f"Total cases audited: {total_audited}")
print(f"  GT=correct:   {total_correct}")
print(f"  GT=partial:   {total_partial}")
print(f"  GT=undefined: {total_undefined}")

print(f"\n{'='*80}")
print("MISLABELED: GT=correct but contains partial signal text")
print(f"{'='*80}")
print(f"Count: {len(mislabeled_correct)}")
for case_id, seed, gt, sig, prompt in mislabeled_correct[:20]:
    print(f"  [{seed}] {case_id} | Signal: {sig}")
    print(f"    {prompt}...")

print(f"\n{'='*80}")
print("MISLABELED: GT=partial but contains correct signal text")
print(f"{'='*80}")
print(f"Count: {len(mislabeled_partial)}")
for case_id, seed, gt, sig, prompt in mislabeled_partial[:20]:
    print(f"  [{seed}] {case_id} | Signal: {sig}")
    print(f"    {prompt}...")

print(f"\n{'='*80}")
print("MISLABELED: GT=partial but contains undefined signal text (should be undefined)")
print(f"{'='*80}")
print(f"Count: {len(mislabeled_undefined)}")
for case_id, seed, gt, sig, prompt in mislabeled_undefined[:20]:
    print(f"  [{seed}] {case_id} | Signal: {sig}")
    print(f"    {prompt}...")

total_issues = len(mislabeled_correct) + len(mislabeled_partial) + len(mislabeled_undefined)
print(f"\n{'='*80}")
print(f"TOTAL MISLABELED: {total_issues}/{total_audited} ({total_issues/total_audited*100:.1f}%)")
print(f"{'='*80}")
