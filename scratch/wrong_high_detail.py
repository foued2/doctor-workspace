import sys
sys.path.insert(0, r'F:\pythonProject')

SOLUTIONS = {
    "Two Sum::correct": ("correct", "Two Sum"),
    "Two Sum::partial": ("partial", "Two Sum"),
    "Two Sum::incorrect": ("incorrect", "Two Sum"),
    "Palindrome Number::correct": ("correct", "Palindrome Number"),
    "Palindrome Number::partial": ("partial", "Palindrome Number"),
    "Palindrome Number::incorrect": ("partial", "Palindrome Number"),
    "Valid Parentheses::correct": ("correct", "Valid Parentheses"),
    "Valid Parentheses::partial": ("incorrect", "Valid Parentheses"),
    "Valid Parentheses::incorrect": ("incorrect", "Valid Parentheses"),
    "Roman to Integer::correct": ("correct", "Roman to Integer"),
    "Roman to Integer::partial": ("incorrect", "Roman to Integer"),
    "Roman to Integer::incorrect": ("incorrect", "Roman to Integer"),
    "Merge Two Sorted Lists::correct": ("correct", "Merge Two Sorted Lists"),
    "Merge Two Sorted Lists::partial": ("partial", "Merge Two Sorted Lists"),
    "Merge Two Sorted Lists::incorrect": ("incorrect", "Merge Two Sorted Lists"),
    "Longest Palindromic Substring::correct": ("correct", "Longest Palindromic Substring"),
    "Longest Palindromic Substring::partial": ("incorrect", "Longest Palindromic Substring"),
    "Longest Palindromic Substring::incorrect": ("incorrect", "Longest Palindromic Substring"),
    "Container With Most Water::correct": ("correct", "Container With Most Water"),
    "Container With Most Water::partial": ("partial", "Container With Most Water"),
    "Container With Most Water::incorrect": ("incorrect", "Container With Most Water"),
    "Trapping Rain Water::correct": ("correct", "Trapping Rain Water"),
    "Trapping Rain Water::partial": ("incorrect", "Trapping Rain Water"),
    "Trapping Rain Water::incorrect": ("incorrect", "Trapping Rain Water"),
    "N-Queens::correct": ("correct", "N-Queens"),
    "N-Queens::partial": ("partial", "N-Queens"),
    "N-Queens::incorrect": ("incorrect", "N-Queens"),
}

from doctor.llm_doctor import predict

wrong_high = []
all_high = []

for key, (gt, prob) in sorted(SOLUTIONS.items()):
    case_id = f"{prob.replace(' ', '_')}_{key.split('::')[1]}"
    # Quick read the solution code from the baseline file
    pass

# Instead, just re-run predictions for the 27 cases using a direct import
# Read the SOLUTIONS dict from the actual test file
exec(compile(open(r'F:\pythonProject\tests\verify_code_only_baseline.py', encoding='utf-8').read(), 
             r'F:\pythonProject\tests\verify_code_only_baseline.py', 'exec'), globals())

from external_stress_layer import StressCase, StressKind

doctor_cases = []
for key, sol in sorted(SOLUTIONS.items()):
    problem_name, sol_type = key.split("::")
    prompt = f"PROBLEM: {sol['problem']}\n\nSOLUTION:\n{sol['code']}"
    doctor_cases.append((
        f"{problem_name.replace(' ', '_')}_{sol_type}",
        prompt,
        sol["ground_truth"],
    ))

print("=" * 120)
print("HIGH-CONFIDENCE VERDICTS (confidence >= 0.70)")
print("=" * 120)
print(f"{'Case':<45} {'GT':<12} {'Pred':<12} {'Conf':>6} {'Status'}")
print("-" * 120)

from doctor.llm_doctor import LLMDoctor
doctor = LLMDoctor()

for case_id, prompt, gt in doctor_cases:
    pred = doctor.predict(prompt)
    conf = pred.get('confidence', 0) or 0
    label = pred['label']
    correct = (label == gt)
    
    if conf >= 0.70:
        status = "CORRECT" if correct else "** WRONG **"
        print(f"{case_id:<45} {gt:<12} {label:<12} {conf:>6.2f} {status}")
        all_high.append(case_id)
        if not correct:
            bi = pred.get('system_bias_indicators', {})
            wrong_high.append({
                'case': case_id, 'gt': gt, 'pred': label, 'conf': conf,
                'l1': bi.get('layer1_verdict'),
                'l2': bi.get('layer2_verdict'),
                'severity': bi.get('layer2_severity'),
                'ratio': bi.get('layer2_failure_ratio'),
                'core': bi.get('layer2_core_failures'),
                'edge': bi.get('layer2_edge_failures'),
                'l2_fails': bi.get('layer2_failures'),
                'decision': pred.get('decision_path'),
                'kind': pred.get('confidence_kind'),
            })

print("-" * 120)
print(f"High-conf total: {len(all_high)} | Wrong@HighConf: {len(wrong_high)}")
if all_high:
    print(f"Wrong@HighConf rate: {len(wrong_high)/len(all_high)*100:.1f}%")

if wrong_high:
    print(f"\n{'=' * 120}")
    print("WRONG @ HIGH CONF — DETAILED")
    print("=" * 120)
    for w in wrong_high:
        print(f"\n  Case:        {w['case']}")
        print(f"  GT={w['gt']}  ->  Pred={w['pred']}  conf={w['conf']:.2f}  kind={w['kind']}")
        print(f"  L1={w['l1']}  L2={w['l2']}  severity={w['severity']}  ratio={w['ratio']}")
        print(f"  core_fail={w['core']}  edge_fail={w['edge']}")
        print(f"  L2_fails:    {w['l2_fails']}")
        print(f"  Decision:    {w['decision']}")
