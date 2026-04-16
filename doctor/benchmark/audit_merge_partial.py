"""Audit what L2 produces for Merge_Two_Sorted_Lists_partial."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'F:\pythonProject')

from doctor.core.test_executor import TestExecutor, make_list, list_to_vals

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

executor = TestExecutor()
report = executor.verify("Merge Two Sorted Lists", code)

print(f"Verdict: {report.verdict}")
print(f"Pass rate: {report.pass_rate} ({report.passed}/{report.total})")
print()
for r in report.results:
    print(f"  {r.label:20s} passed={r.passed}  got={r.got}  expected={r.expected}")
print()
print(f"Failure type: {report.failure_type}")
print(f"Core failures: {report.core_failures}, Edge failures: {report.edge_failures}")
