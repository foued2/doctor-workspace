"""Reproduce baseline exact conditions for Merge partial."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'F:\pythonProject')

# Import everything the baseline imports
from doctor.llm_doctor import LLMDoctor, _extract_problem_and_solution
from external_stress_layer import StressCase, StressKind

# The exact prompt the baseline uses
sol = {
    "problem": "Merge two sorted linked lists and return it as a sorted list.",
    "code": (
        "def mergeTwoLists(list1, list2):\n"
        "    vals = []\n"
        "    curr = list1\n"
        "    while curr:\n"
        "        vals.append(curr.val)\n"
        "        curr = curr.next\n"
        "    curr = list2\n"
        "    while curr:\n"
        "        vals.append(curr.val)\n"
        "        curr = curr.next\n"
        "    vals.sort()\n"
        "    dummy = ListNode(0)\n"
        "    curr = dummy\n"
        "    for v in vals:\n"
        "        curr.next = ListNode(v)\n"
        "        curr = curr.next\n"
        "    return dummy.next"
    ),
}
problem_name = "Merge Two Sorted Lists"
sol_type = "partial"
prompt = f"PROBLEM: {sol['problem']}\n\nSOLUTION:\n{sol['code']}"

case = StressCase(
    case_id=f"{problem_name.replace(' ', '_')}_{sol_type}",
    prompt=prompt,
    stress_kind=StressKind.MIXED,
    ground_truth="partial",
)

# Run through the same pipeline as baseline
doctor = LLMDoctor()
pred = doctor.predict(case.prompt)

print(f"Case: {case.case_id}")
print(f"Label: {pred['label']}")
print(f"Confidence: {pred['confidence']}")
print(f"Kind: {pred['confidence_kind']}")
print(f"Decision path: {pred['decision_path']}")
l2 = pred.get('system_bias_indicators', {})
print(f"L2 verdict: {l2.get('layer2_verdict')}")
print(f"L2 pass_rate: {l2.get('layer2_pass_rate')}")
print(f"L2 failures: {l2.get('layer2_failures')}")
print(f"L1 verdict: {l2.get('layer1_verdict')}")
print(f"L1 violations: {l2.get('layer1_violations')}")
