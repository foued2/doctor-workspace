#!/usr/bin/env python
"""
Blind Doctor Test — 3 real LeetCode problems × 3 real solutions.
No labels. No solution type markers. No hints.
Just problem statement + code.
"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from doctor.llm_doctor import LLMDoctor

PROBLEMS = {
    "Two Sum": {
        "description": (
            "Given an array of integers nums and an integer target, "
            "return indices of the two numbers such that they add up to target. "
            "You may assume that each input would have exactly one solution, "
            "and you may not use the same element twice. "
            "You can return the answer in any order."
        ),
        "solutions": {
            "correct": (
                "def twoSum(nums, target):\n"
                "    seen = {}\n"
                "    for i, n in enumerate(nums):\n"
                "        if target - n in seen:\n"
                "            return [seen[target-n], i]\n"
                "        seen[n] = i"
            ),
            "subtly_wrong": (
                "def twoSum(nums, target):\n"
                "    seen = {}\n"
                "    for i, n in enumerate(nums):\n"
                "        seen[n] = i\n"
                "        if target - n in seen:\n"
                "            return [seen[target-n], i]"
            ),
            "incorrect": (
                "def twoSum(nums, target):\n"
                "    for i in range(len(nums)):\n"
                "        for j in range(len(nums)):\n"
                "            if nums[i] + nums[j] == target:\n"
                "                return [i, j]"
            ),
        },
    },
    "Valid Parentheses": {
        "description": (
            "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', "
            "determine if the input string is valid.\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order.\n"
            "3. Every close bracket has a corresponding open bracket of the same type."
        ),
        "solutions": {
            "correct": (
                "def isValid(s):\n"
                "    stack = []\n"
                "    mapping = {')':'(', '}':'{', ']':'['}\n"
                "    for char in s:\n"
                "        if char in mapping:\n"
                "            top = stack.pop() if stack else '#'\n"
                "            if mapping[char] != top:\n"
                "                return False\n"
                "        else:\n"
                "            stack.append(char)\n"
                "    return not stack"
            ),
            "subtly_wrong": (
                "def isValid(s):\n"
                "    stack = []\n"
                "    mapping = {')':'(', '}':'{', ']':'['}\n"
                "    for char in s:\n"
                "        if char in mapping:\n"
                "            top = stack.pop() if stack else '#'\n"
                "            if mapping[char] != top:\n"
                "                return False\n"
                "        else:\n"
                "            stack.append(char)\n"
                "    return True"
            ),
            "incorrect": (
                "def isValid(s):\n"
                "    while '()' in s or '{}' in s or '[]' in s:\n"
                "        s = s.replace('()','').replace('{}','').replace('[]','')\n"
                "    return s == ''"
            ),
        },
    },
    "Maximum Subarray": {
        "description": (
            "Given an integer array nums, find the subarray with the largest sum, "
            "and return its sum."
        ),
        "solutions": {
            "correct": (
                "def maxSubArray(nums):\n"
                "    max_sum = current = nums[0]\n"
                "    for n in nums[1:]:\n"
                "        current = max(n, current + n)\n"
                "        max_sum = max(max_sum, current)\n"
                "    return max_sum"
            ),
            "subtly_wrong": (
                "def maxSubArray(nums):\n"
                "    max_sum = current = 0\n"
                "    for n in nums:\n"
                "        current = max(n, current + n)\n"
                "        max_sum = max(max_sum, current)\n"
                "    return max_sum"
            ),
            "incorrect": (
                "def maxSubArray(nums):\n"
                "    return max(sum(nums[i:j])\n"
                "               for i in range(len(nums))\n"
                "               for j in range(i+1, len(nums)+1))"
            ),
        },
    },
}


def main():
    doctor = LLMDoctor()
    total = 0
    correct = 0
    results = []

    print("=" * 70)
    print("BLIND DOCTOR TEST — 3 Problems x 3 Solutions (No Labels)")
    print("=" * 70)

    for prob_name, prob_data in PROBLEMS.items():
        print(f"\n{'─'*70}")
        print(f"  PROBLEM: {prob_name}")
        print(f"{'─'*70}")

        for verdict_key, code in prob_data["solutions"].items():
            total += 1
            prompt = f"PROBLEM: {prob_data['description']}\n\nSOLUTION:\n{code}"
            result = doctor.predict(prompt)
            predicted = result["label"]
            confidence = result["confidence"]
            bias = result.get("system_bias_indicators", {})
            reasoning = bias.get("llm_reasoning", "")
            issues = bias.get("llm_issues", [])
            source = bias.get("llm_source", "unknown")

            match = predicted == verdict_key
            if match:
                correct += 1

            marker = "✓" if match else "✗"
            print(f"\n  [{marker}] Expected: {verdict_key:16s} → Got: {predicted:12s} (conf={confidence:.2f})")
            if reasoning:
                print(f"      Reasoning: {reasoning}")
            if issues:
                print(f"      Issues:    {issues}")
            print(f"      Source:    {source}")

            results.append({
                "problem": prob_name,
                "expected": verdict_key,
                "predicted": predicted,
                "confidence": confidence,
                "reasoning": reasoning,
                "issues": issues,
                "correct": match,
            })

    print(f"\n{'='*70}")
    print(f"RESULTS: {correct}/{total} ({correct/total*100:.0f}%)")
    print(f"{'='*70}")

    # Per-problem breakdown
    by_problem = {}
    for r in results:
        p = r["problem"]
        if p not in by_problem:
            by_problem[p] = {"total": 0, "correct": 0}
        by_problem[p]["total"] += 1
        if r["correct"]:
            by_problem[p]["correct"] += 1

    print(f"\nPer-problem:")
    for p, d in by_problem.items():
        print(f"  {p}: {d['correct']}/{d['total']}")

    # By expected verdict
    by_verdict = {}
    for r in results:
        v = r["expected"]
        if v not in by_verdict:
            by_verdict[v] = {"total": 0, "correct": 0}
        by_verdict[v]["total"] += 1
        if r["correct"]:
            by_verdict[v]["correct"] += 1

    print(f"\nBy verdict type:")
    for v in ["correct", "subtly_wrong", "incorrect"]:
        d = by_verdict.get(v, {"total": 0, "correct": 0})
        print(f"  {v:16s}: {d['correct']}/{d['total']}")


if __name__ == "__main__":
    main()
