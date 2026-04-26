import json

from doctor.run_doctor import run_doctor


TWO_SUM_STATEMENT = (
    "I have a list of numbers and a target number. "
    "I need to find which two numbers in the list add up to the target. "
    "There's always exactly one answer."
)

CORRECT_TWO_SUM = """
def twoSum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []
""".strip()

WRONG_TWO_SUM = """
def twoSum(nums, target):
    return []
""".strip()


def main() -> None:
    correct = run_doctor(TWO_SUM_STATEMENT, CORRECT_TWO_SUM)
    wrong = run_doctor(TWO_SUM_STATEMENT, WRONG_TWO_SUM)

    assert correct["status"] == "verified", correct
    assert correct["problem_id"] == "two_sum", correct
    assert correct["verdict"] == "correct", correct

    assert wrong["status"] == "verified", wrong
    assert wrong["problem_id"] == "two_sum", wrong
    assert wrong["verdict"] in {"partial", "incorrect"}, wrong

    print("correct_case")
    print(json.dumps(correct, indent=2))
    print("wrong_case")
    print(json.dumps(wrong, indent=2))


if __name__ == "__main__":
    main()
