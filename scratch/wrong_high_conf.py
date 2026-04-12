import sys
sys.path.insert(0, r'F:\pythonProject')
from collections import defaultdict

from doctor.llm_doctor import LLMDoctor, _extract_problem_and_solution
from external_stress_layer import StressCase, StressKind

# Import the same SOLUTIONS from the baseline test
exec(open(r'F:\pythonProject\tests\verify_code_only_baseline.py', encoding='utf-8').read())

doctor = LLMDoctor()

cases = []
for key, sol in sorted(SOLUTIONS.items()):
    problem_name, sol_type = key.split("::")
    prompt = f"PROBLEM: {sol['problem']}\n\nSOLUTION:\n{sol['code']}"
    cases.append(StressCase(
        case_id=f"{problem_name.replace(' ', '_')}_{sol_type}",
        prompt=prompt,
        stress_kind=StressKind.MIXED,
        ground_truth=sol["ground_truth"],
    ))

print("=" * 100)
print("HIGH-CONFIDENCE VERDICTS (confidence >= 0.70)")
print("=" * 100)
print(f"{'Case':<45} {'GT':<12} {'Pred':<12} {'Conf':>6} {'Status'}")
print("-" * 100)

high_conf_cases = []
wrong_high = []

for case in cases:
    pred = doctor.predict(case.prompt)
    conf = pred.get('confidence', 0) or 0
    label = pred['label']
    gt = case.ground_truth
    correct = (label == gt)

    if conf >= 0.70:
        status = "CORRECT" if correct else "WRONG"
        print(f"{case.case_id:<45} {gt:<12} {label:<12} {conf:>6.2f} {status}")
        high_conf_cases.append((case, pred))
        if not correct:
            wrong_high.append((case, pred))

print("-" * 100)
print(f"\nTotal high-confidence cases: {len(high_conf_cases)}")
print(f"Wrong @ high conf: {len(wrong_high)}")
print(f"Wrong@HighConf rate: {len(wrong_high)/len(high_conf_cases)*100:.1f}%")

if wrong_high:
    print(f"\n{'=' * 100}")
    print("WRONG @ HIGH CONF — DETAILED BREAKDOWN")
    print("=" * 100)
    for case, pred in wrong_high:
        bi = pred.get('system_bias_indicators', {})
        print(f"\n  Case:        {case.case_id}")
        print(f"  GT:          {case.ground_truth}")
        print(f"  Pred:        {pred['label']}")
        print(f"  Confidence:  {pred['confidence']}")
        print(f"  Conf Kind:   {pred.get('confidence_kind')}")
        print(f"  L1 Verdict:  {bi.get('layer1_verdict')}")
        print(f"  L2 Verdict:  {bi.get('layer2_verdict')}")
        print(f"  Severity:    {bi.get('layer2_severity')}")
        print(f"  Fail Ratio:  {bi.get('layer2_failure_ratio')}")
        print(f"  Core Fail:   {bi.get('layer2_core_failures')}")
        print(f"  Edge Fail:   {bi.get('layer2_edge_failures')}")
        print(f"  L2 Failures: {bi.get('layer2_failures')}")
        print(f"  Decision:    {pred.get('decision_path')}")
