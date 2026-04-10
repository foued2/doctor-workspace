"""
Debug script: Extract and analyze misclassified undefined->partial cases.
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

# Analyze misclassified cases
for i, (case, pred) in enumerate(misclassified):
    print(f'=== Case {i+1}: {case.case_id} ===')
    print(f'Stress kind: {case.stress_kind}')
    print(f'Ground truth: {case.ground_truth}')
    print(f'Predicted: {pred["label"]} (confidence: {pred["confidence"]})')
    print(f'Decision path: {pred.get("decision_path", "N/A")}')
    print(f'Priority rule: {pred.get("priority_rule_applied", "None")}')
    print(f'Conflict detected: {pred.get("conflict_detected", False)}')
    print()
    print(f'Prompt:')
    print(case.prompt)
    print()
    print('-' * 80)
    print()

# Now analyze what signals are present
print('\n=== SIGNAL ANALYSIS ===\n')
from doctor.undefined_detection import detect_undefined, undefined_score

for i, (case, pred) in enumerate(misclassified):
    signals = detect_undefined(case.prompt)
    score = undefined_score(signals)
    
    print(f'Case {case.case_id}:')
    print(f'  Undefined score: {score}')
    print(f'  Signals detected: {len(signals)}')
    for sig in signals[:5]:  # Top 5 signals
        print(f'    - {sig.category}: {sig.pattern} (strength={sig.strength})')
    print()
