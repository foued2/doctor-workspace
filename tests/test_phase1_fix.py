"""
Test script: Verify Phase 1 undefined detection fix.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from doctor.raw_prompt_doctor import RawPromptDoctor
from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks

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

doctor = RawPromptDoctor()
cases = generate_esl_cases(n=60, seed=42)

# Filter to undefined ground truth cases
undefined_cases = [c for c in cases if c.ground_truth == 'undefined']

print(f'Total ESL cases: {len(cases)}')
print(f'Total undefined cases: {len(undefined_cases)}')
print()

# Run predictions and find misclassified
misclassified = []
correctly_classified = []

for case in undefined_cases:
    pred = doctor.predict(case.prompt)
    if pred['label'] == 'undefined':
        correctly_classified.append((case, pred))
    else:
        misclassified.append((case, pred))

print(f'Correctly classified as undefined: {len(correctly_classified)}')
print(f'Misclassified (not undefined): {len(misclassified)}')
print()

# Calculate undefined recall
undefined_recall = len(correctly_classified) / len(undefined_cases) if undefined_cases else 0.0
print(f'Undefined recall: {undefined_recall:.2%} ({len(correctly_classified)}/{len(undefined_cases)})')
print()

if misclassified:
    print('=== REMAINING MISCLASSIFIED CASES ===')
    for i, (case, pred) in enumerate(misclassified):
        print(f'\nCase {i+1}: {case.case_id}')
        print(f'  Predicted: {pred["label"]} (confidence: {pred["confidence"]})')
        print(f'  Decision path: {pred.get("decision_path", "N/A")}')
        print(f'  Prompt (first 200 chars): {case.prompt[:200]}...')
else:
    print('SUCCESS! All undefined cases now correctly classified!')

print()
print('=== PHASE 1 TARGET: undefined recall > 70% ===')
if undefined_recall > 0.70:
    print(f'✓ TARGET ACHIEVED: {undefined_recall:.2%} > 70%')
else:
    print(f'✗ TARGET NOT MET: {undefined_recall:.2%} < 70%')
