"""Debug: run all 3 Merge cases and show L2 reports."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'F:\pythonProject')

from doctor.core.test_executor import TestExecutor, make_list, list_to_vals

SOLUTIONS = {
    "Merge Two Sorted Lists::correct": (
        "def mergeTwoLists(list1, list2):\n"
        "    dummy = ListNode(0)\n"
        "    curr = dummy\n"
        "    while list1 and list2:\n"
        "        if list1.val <= list2.val:\n"
        "            curr.next = list1\n"
        "            list1 = list1.next\n"
        "        else:\n"
        "            curr.next = list2\n"
        "            list2 = list2.next\n"
        "        curr = curr.next\n"
        "    curr.next = list1 if list1 else list2\n"
        "    return dummy.next"
    ),
    "Merge Two Sorted Lists::partial": (
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
    "Merge Two Sorted Lists::incorrect": (
        "def mergeTwoLists(list1, list2):\n"
        "    if not list1:\n"
        "        return list2\n"
        "    if not list2:\n"
        "        return list1\n"
        "    while list1 and list2:\n"
        "        if list1.val <= list2.val:\n"
        "            list1 = list1.next\n"
        "        else:\n"
        "            list2 = list2.next\n"
        "    return list1"
    ),
}

executor = TestExecutor()

for key, code in sorted(SOLUTIONS.items()):
    print(f"\n{'='*60}")
    print(f"  {key}")
    print(f"{'='*60}")
    report = executor.verify("Merge Two Sorted Lists", code)
    print(f"  Verdict: {report.verdict}")
    print(f"  Pass rate: {report.pass_rate} ({report.passed}/{report.total})")
    for r in report.results:
        got_vals = list_to_vals(r.got) if r.got else None
        print(f"    {r.label:20s} pass={r.passed}  got={got_vals}  exp={r.expected}")
    if report.error:
        print(f"  ERROR: {report.error}")
