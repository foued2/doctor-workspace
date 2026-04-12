import sys
sys.path.insert(0, r'F:\pythonProject')
from doctor.test_executor import TestExecutor

# The correct merge solution from the baseline
correct_merge = """def mergeTwoLists(list1, list2):
    dummy = ListNode(0)
    curr = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            curr.next = list1
            list1 = list1.next
        else:
            curr.next = list2
            list2 = list2.next
        curr = curr.next
    curr.next = list1 if list1 else list2
    return dummy.next"""

executor = TestExecutor()
report = executor.verify("Merge Two Sorted Lists", correct_merge)
print(f"Correct merge: verdict={report.verdict}, pass_rate={report.pass_rate}")
print(f"  severity={report.severity}, ratio={report.failure_ratio}")
print(f"  core_fail={report.core_failures}, edge_fail={report.edge_failures}")
for r in report.results:
    status = "PASS" if r.passed else "FAIL"
    print(f"  [{status}] {r.label}: got={r.got}, expected={r.expected}")
