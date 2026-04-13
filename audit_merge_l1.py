"""Audit why Merge_Two_Sorted_Lists_partial is predicted as incorrect."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'F:\pythonProject')

problem = "Merge two sorted linked lists and return it as a sorted list."
code = (
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
)

from doctor.code_analyzer import CodeAnalyzer
analyzer = CodeAnalyzer()
result = analyzer.analyze(problem, code, problem_name="Merge Two Sorted Lists")

print(f"Verdict: {result.verdict}")
print(f"Confidence: {result.confidence}")
print(f"Failures: {result.failures}")
print(f"Details:")
for k, v in result.details.items():
    status = "PASS" if v else "FAIL"
    print(f"  {status}  {k}")
print(f"Fatal flags: {result.fatal_flags}")
print(f"Reasoning: {result.reasoning}")
