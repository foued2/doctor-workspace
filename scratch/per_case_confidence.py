"""Per-case confidence breakdown for all 27 baseline cases."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'F:\\pythonProject')

from collections import defaultdict
from doctor.llm_doctor import LLMDoctor, _extract_problem_and_solution
from external_stress_layer import StressCase, StressKind
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator
from doctor.doctor_grader import DoctorGrader

# Import the SOLUTIONS dict from the baseline test
from tests.verify_code_only_baseline import SOLUTIONS

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

print("=" * 80)
print("PER-CASE CONFIDENCE BREAKDOWN")
print("=" * 80)

predictions = []
for case in cases:
    pred = doctor.predict(case.prompt)
    predictions.append(pred)

evaluator = EnhancedEvaluator()
metrics = evaluator.evaluate_batch(cases, predictions)
grader = DoctorGrader()
result = grader.grade(cases, predictions, metrics.distribution_shift)

wrong_at_high = []
all_wrong = []

for case, pred in zip(cases, predictions):
    name = case.case_id
    gt = case.ground_truth
    pred_label = pred["label"]
    conf = pred.get("confidence")
    kind = pred.get("kind", "?")
    l1 = pred.get("l1_verdict", "?")
    l2 = pred.get("l2_verdict", "?")
    l2_fail = pred.get("l2_fail", [])
    viol = pred.get("rule_violations", [])
    matched = (gt == pred_label)
    
    if not matched:
        all_wrong.append({
            "name": name, "gt": gt, "pred": pred_label,
            "conf": conf, "kind": kind, "l1": l1, "l2": l2,
            "l2_fail": l2_fail, "viol": viol
        })
        if conf is not None and conf >= 0.7:
            wrong_at_high.append({
                "name": name, "gt": gt, "pred": pred_label,
                "conf": conf, "kind": kind, "l1": l1, "l2": l2,
                "l2_fail": l2_fail, "viol": viol
            })

    conf_str = f"{conf:.2f}" if conf is not None else "N/A"
    flag = " <<< WRONG@HIGH" if (not matched and conf is not None and conf >= 0.7) else ""
    status = "✓" if matched else "✗"
    
    print(f"\n{status} {name}{flag}")
    print(f"  GT={gt} → Pred={pred_label}  conf={conf_str}  kind={kind}")
    print(f"  L1={l1} | L2={l2} | L2_fail={l2_fail}")
    if viol:
        print(f"  Violations={viol}")

print(f"\n{'=' * 80}")
print(f"WRONG@HIGH-CONF CASES (conf >= 0.7 AND wrong): {len(wrong_at_high)}")
for r in wrong_at_high:
    print(f"  ✗ {r['name']}: GT={r['gt']} → Pred={r['pred']} (conf={r['conf']:.2f})")
    print(f"     kind={r['kind']} L1={r['l1']} L2={r['l2']} L2_fail={r['l2_fail']}")

print(f"\n{'=' * 80}")
print(f"ALL MISCLASSIFIED CASES (sorted by confidence desc)")
all_wrong.sort(key=lambda x: x.get('conf') or 0, reverse=True)
for r in all_wrong:
    conf_str = f"{r['conf']:.2f}" if r['conf'] is not None else "N/A"
    print(f"  {r['name']}: GT={r['gt']} → Pred={r['pred']} (conf={conf_str})  kind={r['kind']}")

# Save to scratch
output = {
    "wrong_at_high_conf": wrong_at_high,
    "all_misclassified": all_wrong,
    "summary": {
        "total_cases": len(cases),
        "wrong_at_high_count": len(wrong_at_high),
        "wrong_at_high_pct": f"{len(wrong_at_high)/len(cases)*100:.1f}%",
    }
}
import json
out_path = os.path.join('F:\\pythonProject', 'scratch', 'per_case_confidence.json')
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved to {out_path}")
