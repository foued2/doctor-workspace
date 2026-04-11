"""
Code-Only Baseline — Doctor evaluated with actual Python solution code.

Each case has a real LeetCode problem description + executable Python solution.
This is the input format the Doctor was designed for.
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from collections import defaultdict
from pathlib import Path

from doctor.llm_doctor import LLMDoctor, _extract_problem_and_solution
from doctor.code_analyzer import CodeAnalyzer
from doctor.test_executor import TestExecutor, PROBLEM_KEY_MAP
from doctor.undefined_detection import classify_undefined
from external_stress_layer import StressCase, StressKind
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator
from doctor.doctor_grader import DoctorGrader


# ===========================================================================
# 10 problems × 3 solution types = 30 cases with real code
# ===========================================================================

SOLUTIONS = {
    # ─── Two Sum ──────────────────────────────────────────────────
    "Two Sum::correct": {
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.",
        "code": (
            "def twoSum(nums, target):\n"
            "    seen = {}\n"
            "    for i, n in enumerate(nums):\n"
            "        complement = target - n\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "        seen[n] = i\n"
            "    return []"
        ),
        "ground_truth": "correct",
    },
    "Two Sum::partial": {
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.",
        "code": (
            "def twoSum(nums, target):\n"
            "    for i in range(len(nums)):\n"
            "        for j in range(i + 1, len(nums)):\n"
            "            if nums[i] + nums[j] == target:\n"
            "                return [i, j]\n"
            "    return []"
        ),
        "ground_truth": "partial",
    },
    "Two Sum::incorrect": {
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.",
        "code": (
            "def twoSum(nums, target):\n"
            "    for i in range(len(nums)):\n"
            "        if nums[i] + nums[i] == target:\n"
            "            return [i, i]\n"
            "    return []"
        ),
        "ground_truth": "incorrect",
    },

    # ─── Palindrome Number ────────────────────────────────────────
    "Palindrome Number::correct": {
        "problem": "Given an integer x, return true if x is a palindrome integer, and false otherwise. Do not convert the integer to a string.",
        "code": (
            "def isPalindrome(x):\n"
            "    if x < 0:\n"
            "        return False\n"
            "    if x % 10 == 0 and x != 0:\n"
            "        return False\n"
            "    rev = 0\n"
            "    orig = x\n"
            "    while x > 0:\n"
            "        rev = rev * 10 + x % 10\n"
            "        x //= 10\n"
            "    return rev == orig"
        ),
        "ground_truth": "correct",
    },
    "Palindrome Number::partial": {
        "problem": "Given an integer x, return true if x is a palindrome integer, and false otherwise.",
        "code": (
            "def isPalindrome(x):\n"
            "    return str(x) == str(x)[::-1]"
        ),
        "ground_truth": "partial",
    },
    "Palindrome Number::incorrect": {
        "problem": "Given an integer x, return true if x is a palindrome integer, and false otherwise.",
        "code": (
            "def isPalindrome(x):\n"
            "    return str(abs(x)) == str(abs(x))[::-1]"
        ),
        "ground_truth": "partial",  # abs() is only flaw — handles positives correctly
    },

    # ─── Valid Parentheses ────────────────────────────────────────
    "Valid Parentheses::correct": {
        "problem": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if open brackets must be closed by the same type of brackets and in the correct order.",
        "code": (
            "def isValid(s):\n"
            "    stack = []\n"
            "    mapping = {')': '(', '}': '{', ']': '['}\n"
            "    for char in s:\n"
            "        if char in mapping:\n"
            "            top = stack.pop() if stack else '#'\n"
            "            if mapping[char] != top:\n"
            "                return False\n"
            "        else:\n"
            "            stack.append(char)\n"
            "    return not stack"
        ),
        "ground_truth": "correct",
    },
    "Valid Parentheses::partial": {
        "problem": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        "code": (
            "def isValid(s):\n"
            "    count = {'(': 0, ')': 0, '{': 0, '}': 0, '[': 0, ']': 0}\n"
            "    for c in s:\n"
            "        count[c] += 1\n"
            "    return count['('] == count[')'] and count['{'] == count['}'] and count['['] == count[']']"
        ),
        "ground_truth": "incorrect",  # Counting can't detect order — fundamental flaw
    },
    "Valid Parentheses::incorrect": {
        "problem": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        "code": (
            "def isValid(s):\n"
            "    return len(s) % 2 == 0"
        ),
        "ground_truth": "incorrect",
    },

    # ─── Roman to Integer ─────────────────────────────────────────
    "Roman to Integer::correct": {
        "problem": "Given a roman numeral string s, convert it to an integer. Roman numerals are usually written from largest to smallest left to right, but sometimes a smaller numeral precedes a larger one for subtraction (e.g., IV = 4).",
        "code": (
            "def romanToInt(s):\n"
            "    roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n"
            "    total = 0\n"
            "    for i in range(len(s)):\n"
            "        if i + 1 < len(s) and roman[s[i]] < roman[s[i + 1]]:\n"
            "            total -= roman[s[i]]\n"
            "        else:\n"
            "            total += roman[s[i]]\n"
            "    return total"
        ),
        "ground_truth": "correct",
    },
    "Roman to Integer::partial": {
        "problem": "Given a roman numeral string s, convert it to an integer.",
        "code": (
            "def romanToInt(s):\n"
            "    roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n"
            "    return sum(roman[c] for c in s)"
        ),
        "ground_truth": "incorrect",  # Missing subtractive logic — fundamental flaw
    },
    "Roman to Integer::incorrect": {
        "problem": "Given a roman numeral string s, convert it to an integer.",
        "code": (
            "def romanToInt(s):\n"
            "    mapping = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n"
            "    result = 0\n"
            "    for i in range(len(s) - 1):\n"
            "        if mapping[s[i]] < mapping[s[i+1]]:\n"
            "            result += mapping[s[i+1]] - mapping[s[i]]\n"
            "            s = s[:i] + s[i+2:]\n"
            "    return result + sum(mapping.get(c, 0) for c in s)"
        ),
        "ground_truth": "incorrect",
    },

    # ─── Merge Two Sorted Lists ───────────────────────────────────
    "Merge Two Sorted Lists::correct": {
        "problem": "Merge two sorted linked lists and return it as a sorted list. The list should be made by splicing together the nodes of the first two lists.",
        "code": (
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
        "ground_truth": "correct",
    },
    "Merge Two Sorted Lists::partial": {
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
        "ground_truth": "partial",
    },
    "Merge Two Sorted Lists::incorrect": {
        "problem": "Merge two sorted linked lists and return it as a sorted list.",
        "code": (
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
        "ground_truth": "incorrect",
    },

    # ─── Longest Palindromic Substring ────────────────────────────
    "Longest Palindromic Substring::correct": {
        "problem": "Given a string s, return the longest palindromic substring in s.",
        "code": (
            "def longestPalindrome(s):\n"
            "    if not s:\n"
            "        return ''\n"
            "    start = 0\n"
            "    max_len = 1\n"
            "    for i in range(len(s)):\n"
            "        # Odd length\n"
            "        l, r = i, i\n"
            "        while l >= 0 and r < len(s) and s[l] == s[r]:\n"
            "            if r - l + 1 > max_len:\n"
            "                start = l\n"
            "                max_len = r - l + 1\n"
            "            l -= 1\n"
            "            r += 1\n"
            "        # Even length\n"
            "        l, r = i, i + 1\n"
            "        while l >= 0 and r < len(s) and s[l] == s[r]:\n"
            "            if r - l + 1 > max_len:\n"
            "                start = l\n"
            "                max_len = r - l + 1\n"
            "            l -= 1\n"
            "            r += 1\n"
            "    return s[start:start + max_len]"
        ),
        "ground_truth": "correct",
    },
    "Longest Palindromic Substring::partial": {
        "problem": "Given a string s, return the longest palindromic substring in s.",
        "code": (
            "def longestPalindrome(s):\n"
            "    if not s:\n"
            "        return ''\n"
            "    best = s[0]\n"
            "    for i in range(len(s)):\n"
            "        l, r = i, i\n"
            "        while l >= 0 and r < len(s) and s[l] == s[r]:\n"
            "            if r - l + 1 > len(best):\n"
            "                best = s[l:r+1]\n"
            "            l -= 1\n"
            "            r += 1\n"
            "    return best"
        ),
        "ground_truth": "incorrect",  # Only odd-length palindromes — missing even-length is fundamental flaw
    },
    "Longest Palindromic Substring::incorrect": {
        "problem": "Given a string s, return the longest palindromic substring in s.",
        "code": (
            "def longestPalindrome(s):\n"
            "    seen = {}\n"
            "    best = ''\n"
            "    for i, c in enumerate(s):\n"
            "        if c in seen:\n"
            "            sub = s[seen[c]:i+1]\n"
            "            if len(sub) > len(best):\n"
            "                best = sub\n"
            "        else:\n"
            "            seen[c] = i\n"
            "    return best if best else s[0]"
        ),
        "ground_truth": "incorrect",
    },

    # ─── Container With Most Water ────────────────────────────────
    "Container With Most Water::correct": {
        "problem": "You are given an integer array height of length n. There are n vertical lines. Find two lines that together with the x-axis form a container that holds the most water. Return the maximum amount of water a container can store.",
        "code": (
            "def maxArea(height):\n"
            "    left, right = 0, len(height) - 1\n"
            "    max_water = 0\n"
            "    while left < right:\n"
            "        h = min(height[left], height[right])\n"
            "        max_water = max(max_water, h * (right - left))\n"
            "        if height[left] < height[right]:\n"
            "            left += 1\n"
            "        else:\n"
            "            right -= 1\n"
            "    return max_water"
        ),
        "ground_truth": "correct",
    },
    "Container With Most Water::partial": {
        "problem": "You are given an integer array height of length n. Find two lines that form a container that holds the most water.",
        "code": (
            "def maxArea(height):\n"
            "    max_water = 0\n"
            "    for i in range(len(height)):\n"
            "        for j in range(i + 1, len(height)):\n"
            "            h = min(height[i], height[j])\n"
            "            max_water = max(max_water, h * (j - i))\n"
            "    return max_water"
        ),
        "ground_truth": "partial",
    },
    "Container With Most Water::incorrect": {
        "problem": "You are given an integer array height of length n. Find two lines that form a container that holds the most water.",
        "code": (
            "def maxArea(height):\n"
            "    max_h = max(height)\n"
            "    return max_h * len(height)"
        ),
        "ground_truth": "incorrect",
    },

    # ─── Trapping Rain Water ──────────────────────────────────────
    "Trapping Rain Water::correct": {
        "problem": "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
        "code": (
            "def trap(height):\n"
            "    if not height:\n"
            "        return 0\n"
            "    n = len(height)\n"
            "    left_max = [0] * n\n"
            "    right_max = [0] * n\n"
            "    left_max[0] = height[0]\n"
            "    for i in range(1, n):\n"
            "        left_max[i] = max(left_max[i-1], height[i])\n"
            "    right_max[n-1] = height[n-1]\n"
            "    for i in range(n-2, -1, -1):\n"
            "        right_max[i] = max(right_max[i+1], height[i])\n"
            "    total = 0\n"
            "    for i in range(n):\n"
            "        total += min(left_max[i], right_max[i]) - height[i]\n"
            "    return total"
        ),
        "ground_truth": "correct",
    },
    "Trapping Rain Water::partial": {
        "problem": "Given n non-negative integers representing an elevation map, compute how much water it can trap after raining.",
        "code": (
            "def trap(height):\n"
            "    if len(height) < 3:\n"
            "        return 0\n"
            "    total = 0\n"
            "    for i in range(1, len(height) - 1):\n"
            "        local_max = max(height[i-1], height[i+1])\n"
            "        if height[i] < local_max:\n"
            "            total += local_max - height[i]\n"
            "    return total"
        ),
        "ground_truth": "incorrect",  # Local-max approach is wrong algorithm — fundamental flaw
    },
    "Trapping Rain Water::incorrect": {
        "problem": "Given n non-negative integers representing an elevation map, compute how much water it can trap after raining.",
        "code": (
            "def trap(height):\n"
            "    total = 0\n"
            "    for i in range(1, len(height)):\n"
            "        total += abs(height[i] - height[i-1])\n"
            "    return total"
        ),
        "ground_truth": "incorrect",
    },

    # ─── N-Queens ─────────────────────────────────────────────────
    "N-Queens::correct": {
        "problem": "The n-queens puzzle is the problem of placing n queens on an n×n chessboard such that no two queens attack each other. Given an integer n, return all distinct solutions to the n-queens puzzle.",
        "code": (
            "def solveNQueens(n):\n"
            "    results = []\n"
            "    def backtrack(row, cols, diag1, diag2, board):\n"
            "        if row == n:\n"
            "            results.append([''.join(r) for r in board])\n"
            "            return\n"
            "        for col in range(n):\n"
            "            d1 = row - col\n"
            "            d2 = row + col\n"
            "            if col in cols or d1 in diag1 or d2 in diag2:\n"
            "                continue\n"
            "            cols.add(col)\n"
            "            diag1.add(d1)\n"
            "            diag2.add(d2)\n"
            "            board[row][col] = 'Q'\n"
            "            backtrack(row + 1, cols, diag1, diag2, board)\n"
            "            board[row][col] = '.'\n"
            "            cols.remove(col)\n"
            "            diag1.remove(d1)\n"
            "            diag2.remove(d2)\n"
            "    board = [['.'] * n for _ in range(n)]\n"
            "    backtrack(0, set(), set(), set(), board)\n"
            "    return results"
        ),
        "ground_truth": "correct",
    },
    "N-Queens::partial": {
        "problem": "The n-queens puzzle is the problem of placing n queens on an n×n chessboard such that no two queens attack each other. Return all distinct solutions.",
        "code": (
            "def solveNQueens(n):\n"
            "    results = []\n"
            "    def backtrack(row, cols, diag1, diag2, board):\n"
            "        if row == n:\n"
            "            results.append([''.join(r) for r in board])\n"
            "            return True\n"
            "        for col in range(n):\n"
            "            d1 = row - col\n"
            "            d2 = row + col\n"
            "            if col in cols or d1 in diag1 or d2 in diag2:\n"
            "                continue\n"
            "            cols.add(col)\n"
            "            diag1.add(d1)\n"
            "            diag2.add(d2)\n"
            "            board[row][col] = 'Q'\n"
            "            if backtrack(row + 1, cols, diag1, diag2, board):\n"
            "                return True\n"
            "            board[row][col] = '.'\n"
            "            cols.remove(col)\n"
            "            diag1.remove(d1)\n"
            "            diag2.remove(d2)\n"
            "        return False\n"
            "    board = [['.'] * n for _ in range(n)]\n"
            "    backtrack(0, set(), set(), set(), board)\n"
            "    return results"
        ),
        "ground_truth": "partial",
    },
    "N-Queens::incorrect": {
        "problem": "The n-queens puzzle is the problem of placing n queens on an n×n chessboard such that no two queens attack each other. Return all distinct solutions.",
        "code": (
            "def solveNQueens(n):\n"
            "    from itertools import permutations\n"
            "    results = []\n"
            "    for perm in permutations(range(n)):\n"
            "        valid = True\n"
            "        for i in range(n):\n"
            "            for j in range(i + 1, n):\n"
            "                if abs(perm[i] - perm[j]) == j - i:\n"
            "                    valid = False\n"
            "                    break\n"
            "            if not valid:\n"
            "                break\n"
            "        if valid:\n"
            "            board = [['.'] * n for _ in range(n)]\n"
            "            for r, c in enumerate(perm):\n"
            "                board[r][c] = 'Q'\n"
            "            results.append([''.join(r) for r in board])\n"
            "    return results"
        ),
        "ground_truth": "incorrect",
    },
}


def main():
    print("=" * 80)
    print("CODE-ONLY BASELINE — Doctor on actual Python solution code")
    print("=" * 80)

    doctor = LLMDoctor()

    # Build cases
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

    print(f"\nTotal cases: {len(cases)}")
    gt_counts = defaultdict(int)
    for c in cases:
        gt_counts[c.ground_truth] += 1
    for gt, cnt in sorted(gt_counts.items()):
        print(f"  {gt}: {cnt}")

    # Verify extraction succeeds for all
    extract_fails = 0
    for case in cases:
        pt, code = _extract_problem_and_solution(case.prompt)
        if pt is None:
            extract_fails += 1
            print(f"  ✗ Extraction failed: {case.case_id}")
    if extract_fails == 0:
        print(f"  ✓ All {len(cases)} cases extract successfully")
    else:
        print(f"  ✗ {extract_fails} extraction failures")

    # Run predictions
    print(f"\nRunning predictions...")
    predictions = []
    for case in cases:
        pred = doctor.predict(case.prompt)
        predictions.append(pred)

    # Evaluate
    evaluator = EnhancedEvaluator()
    metrics = evaluator.evaluate_batch(cases, predictions)
    grader = DoctorGrader()
    result = grader.grade(cases, predictions, metrics.distribution_shift)
    result["flags"]["correct_by_luck"] = metrics.correct_by_luck_count
    result["flags"]["shift_score"] = metrics.distribution_shift.get("shift_score", 0.0)

    # Confusion Matrix
    print(f"\n{'='*80}")
    print(f"CONFUSION MATRIX — Ground Truth × Predicted")
    print(f"{'='*80}")

    labels_order = ["correct", "partial", "incorrect", "undefined"]
    cm = defaultdict(lambda: defaultdict(int))
    for case, pred in zip(cases, predictions):
        cm[case.ground_truth][pred["label"]] += 1

    header = f"{'GT \\ Pred':<14}"
    for lbl in labels_order:
        header += f"{lbl:>12}"
    header += f"{'Recall':>10}"
    print(header)
    print("-" * len(header))

    for gt_lbl in labels_order:
        row = f"{gt_lbl:<14}"
        gt_total = sum(cm[gt_lbl].values())
        if gt_total == 0:
            row += f"{'(none)':>12}"
            for _ in labels_order[1:]:
                row += f"{'':>12}"
            row += f"{'N/A':>10}"
            print(row)
            continue

        for pred_lbl in labels_order:
            count = cm[gt_lbl][pred_lbl]
            row += f"{count:>12}"

        tp = cm[gt_lbl][gt_lbl]
        recall = tp / gt_total if gt_total > 0 else 0.0
        row += f"{recall:>9.1%}"
        print(row)

    # Per-class breakdown
    bd = result.get("breakdown", {})
    print(f"\n{'='*80}")
    print(f"PER-CLASS METRICS")
    print(f"{'='*80}")
    for cls in ["correct", "partial", "incorrect", "undefined"]:
        f1 = bd.get(f"{cls}_f1", 0)
        rec = bd.get(f"{cls}_recall", 0)
        print(f"  {cls:<12}: F1={f1:.1%}  Recall={rec:.1%}")

    # Overall
    print(f"\n{'='*80}")
    print(f"OVERALL")
    print(f"{'='*80}")
    print(f"  Grade:         {result['grade']:.4f} ({result['grade_letter']})")
    print(f"  Rule Score:    {result['rule_score']:.4f}")
    print(f"  Wrong@HiConf:  {result['flags']['wrong_at_high_conf']*100:.1f}%")
    shift = result['flags'].get('shift_score')
    print(f"  Shift Score:   {shift:.4f}" if shift is not None else "  Shift Score:   N/A")
    print(f"  Correct by luck: {metrics.correct_by_luck_count}")
    print(f"  Wrong w/ violation: {metrics.wrong_with_violation_count}")

    # Misclassified cases detail
    print(f"\n{'='*80}")
    print(f"MISCLASSIFIED CASES")
    print(f"{'='*80}")
    for case, pred in zip(cases, predictions):
        if pred["label"] != case.ground_truth:
            print(f"  {case.case_id}: GT={case.ground_truth} → Pred={pred['label']} "
                  f"(conf={pred['confidence']}, kind={pred['confidence_kind']})")
            bias = pred.get('system_bias_indicators', {})
            l1v = bias.get('layer1_verdict', '')
            l2v = bias.get('layer2_verdict', '')
            l1viol = bias.get('layer1_violations', [])
            l2fps = [f['label'] for f in bias.get('layer2_failures', [])]
            parts = []
            if l1v: parts.append(f"L1={l1v}")
            if l1viol: parts.append(f"viol={l1viol}")
            if l2v: parts.append(f"L2={l2v}")
            if l2fps: parts.append(f"L2_fail={l2fps}")
            if parts: print(f"    {' | '.join(parts)}")

    # Correct cases detail
    print(f"\n{'='*80}")
    print(f"CORRECTLY CLASSIFIED CASES")
    print(f"{'='*80}")
    for case, pred in zip(cases, predictions):
        if pred["label"] == case.ground_truth:
            print(f"  ✓ {case.case_id}: {pred['label']} (conf={pred['confidence']}, kind={pred['confidence_kind']})")

    # Save
    output = {
        "total_cases": len(cases),
        "gt_distribution": dict(gt_counts),
        "confusion_matrix": {gt: dict(preds) for gt, preds in cm.items()},
        "grade": result["grade"],
        "grade_letter": result["grade_letter"],
        "rule_score": result["rule_score"],
        "wrong_at_high_conf": result["flags"]["wrong_at_high_conf"],
        "shift_score": shift,
        "per_class": {
            cls: {"f1": bd.get(f"{cls}_f1", 0), "recall": bd.get(f"{cls}_recall", 0)}
            for cls in labels_order
        },
    }

    out_path = Path(__file__).parent.parent / "code_only_baseline.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
