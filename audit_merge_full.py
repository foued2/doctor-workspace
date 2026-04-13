"""Audit full prediction for Merge_Two_Sorted_Lists_partial."""
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

prompt = f"PROBLEM: {problem}\n\nSOLUTION:\n{code}"

from doctor.llm_doctor import LLMDoctor
doctor = LLMDoctor()
pred = doctor.predict(prompt)

import json
print(json.dumps(pred, indent=2, default=str))
