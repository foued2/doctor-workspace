from doctor.core.sandbox_runner import run_solution_in_sandbox
from doctor.core.test_executor import TestCase as ExecutorTestCase
from doctor.core.test_executor import TestExecutor


def test_executor_runs_solution_in_sandbox():
    code = """
def twoSum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []
"""

    report = TestExecutor().verify("two_sum", code)

    assert report.verdict == "correct"
    assert report.pass_rate == 1.0
    assert report.error == ""


def test_sandbox_parent_timeout_stops_infinite_loop():
    result = run_solution_in_sandbox(
        code="""
def twoSum(nums, target):
    while True:
        pass
""",
        problem_id="two_sum",
        tests=[ExecutorTestCase(input=([2, 7], 9), expected=[0, 1], label="loop")],
        timeout_seconds=2,
        per_test_timeout_seconds=1,
    )

    assert result.ok is False
    assert "sandbox timeout" in result.error


def test_sandbox_rehydrates_linked_list_inputs():
    code = """
def mergeTwoLists(list1, list2):
    vals = []
    cur = list1
    while cur:
        vals.append(cur.val)
        cur = cur.next
    cur = list2
    while cur:
        vals.append(cur.val)
        cur = cur.next
    vals.sort()
    dummy = ListNode(0)
    cur = dummy
    for val in vals:
        cur.next = ListNode(val)
        cur = cur.next
    return dummy.next
"""

    report = TestExecutor().verify("merge_two_sorted_lists", code)

    assert report.verdict == "correct"
    assert report.pass_rate == 1.0
