"""
Run 5 unseen problems through Layer 1 AI (phi3) + Layer 2 execution.

Tests TWO new rules:
1. Hard rule: ai_confidence >= 0.9 AND evidence_strength < 0.4 → suspicious
2. Reasoning consistency: does AI reasoning reference actual code tokens?

Problems NOT in the current 10-problem suite:
  Current suite: Two Sum, Palindrome Number, Roman to Integer,
                 Valid Parentheses, Merge Two Sorted Lists,
                 Longest Palindromic Substring, Container With Most Water,
                 Median of Two Sorted Arrays, Trapping Rain Water, N-Queens.

  These 5: Longest Substring Without Repeating Characters (#3),
           3Sum (#15), Maximum Subarray (#53),
           Climbing Stairs (#70), Group Anagrams (#49).
"""
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'F:\pythonProject')

from doctor.layer1_ai import get_ai_verdict, check_reasoning_matches_code
from doctor.test_executor import TestExecutor
from doctor.evidence import compute_evidence_strength, get_final_label
from doctor.trust import compute_risk

# 5 problems NOT in the current baseline.
# Each problem: (name, description, correct_code, partial_code, incorrect_code)

PROBLEMS = [
    # ── 1. Longest Substring Without Repeating Characters (#3) ──
    (
        "Longest Substring Without Repeating Characters",
        "Given a string s, find the length of the longest substring without repeating characters.",
        # correct: sliding window with set — O(n) time, O(min(n,m)) space
        "def lengthOfLongestSubstring(s):\n"
        "    chars = set()\n"
        "    max_len = left = 0\n"
        "    for right in range(len(s)):\n"
        "        while s[right] in chars:\n"
        "            chars.remove(s[left])\n"
        "            left += 1\n"
        "        chars.add(s[right])\n"
        "        max_len = max(max_len, right - left + 1)\n"
        "    return max_len",
        # partial: brute force O(n^3) — correct answer but too slow for large input
        "def lengthOfLongestSubstring(s):\n"
        "    max_len = 0\n"
        "    for i in range(len(s)):\n"
        "        for j in range(i + 1, len(s) + 1):\n"
        "            sub = s[i:j]\n"
        "            if len(sub) == len(set(sub)):\n"
        "                max_len = max(max_len, len(sub))\n"
        "    return max_len",
        # incorrect: returns length of longest substring with ALL repeating chars (inverted logic)
        "def lengthOfLongestSubstring(s):\n"
        "    from collections import Counter\n"
        "    counts = Counter(s)\n"
        "    return max(counts.values()) if counts else 0",
    ),

    # ── 2. 3Sum (#15) ──
    (
        "3Sum",
        "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0. The solution set must not contain duplicate triplets.",
        # correct: sort + two pointers — O(n^2) time, handles dedup
        "def threeSum(nums):\n"
        "    nums.sort()\n"
        "    res = []\n"
        "    for i in range(len(nums)):\n"
        "        if i > 0 and nums[i] == nums[i-1]:\n"
        "            continue\n"
        "        l, r = i + 1, len(nums) - 1\n"
        "        while l < r:\n"
        "            s = nums[i] + nums[l] + nums[r]\n"
        "            if s < 0:\n"
        "                l += 1\n"
        "            elif s > 0:\n"
        "                r -= 1\n"
        "            else:\n"
        "                res.append([nums[i], nums[l], nums[r]])\n"
        "                while l < r and nums[l] == nums[l+1]:\n"
        "                    l += 1\n"
        "                while l < r and nums[r] == nums[r-1]:\n"
        "                    r -= 1\n"
        "                l += 1\n"
        "                r -= 1\n"
        "    return res",
        # partial: brute force finds triplets but doesn't deduplicate
        "def threeSum(nums):\n"
        "    res = []\n"
        "    for i in range(len(nums)):\n"
        "        for j in range(i+1, len(nums)):\n"
        "            for k in range(j+1, len(nums)):\n"
        "                if nums[i] + nums[j] + nums[k] == 0:\n"
        "                    res.append([nums[i], nums[j], nums[k]])\n"
        "    return res",
        # incorrect: only finds ONE triplet then returns
        "def threeSum(nums):\n"
        "    for i in range(len(nums)):\n"
        "        for j in range(i+1, len(nums)):\n"
        "            for k in range(j+1, len(nums)):\n"
        "                if nums[i] + nums[j] + nums[k] == 0:\n"
        "                    return [[nums[i], nums[j], nums[k]]]\n"
        "    return []",
    ),

    # ── 3. Maximum Subarray (#53) ──
    (
        "Maximum Subarray",
        "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
        # correct: Kadane's algorithm — O(n) time, O(1) space
        "def maxSubArray(nums):\n"
        "    max_sum = curr_sum = nums[0]\n"
        "    for num in nums[1:]:\n"
        "        curr_sum = max(num, curr_sum + num)\n"
        "        max_sum = max(max_sum, curr_sum)\n"
        "    return max_sum",
        # partial: brute force O(n^2) — correct but too slow for n=10^5
        "def maxSubArray(nums):\n"
        "    max_sum = nums[0]\n"
        "    for i in range(len(nums)):\n"
        "        curr = 0\n"
        "        for j in range(i, len(nums)):\n"
        "            curr += nums[j]\n"
        "            max_sum = max(max_sum, curr)\n"
        "    return max_sum",
        # incorrect: returns sum of entire array regardless
        "def maxSubArray(nums):\n"
        "    return sum(nums)",
    ),

    # ── 4. Climbing Stairs (#70) ──
    (
        "Climbing Stairs",
        "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        # correct: DP with O(n) space — fibonacci recurrence
        "def climbStairs(n):\n"
        "    if n <= 3:\n"
        "        return n\n"
        "    dp = [0] * (n + 1)\n"
        "    dp[1], dp[2] = 1, 2\n"
        "    for i in range(3, n + 1):\n"
        "        dp[i] = dp[i-1] + dp[i-2]\n"
        "    return dp[n]",
        # partial: correct recursive solution but exponential time O(2^n)
        "def climbStairs(n):\n"
        "    if n <= 2:\n"
        "        return n\n"
        "    return climbStairs(n-1) + climbStairs(n-2)",
        # incorrect: returns n (just counts steps, not ways)
        "def climbStairs(n):\n"
        "    return n",
    ),

    # ── 5. Group Anagrams (#49) ──
    (
        "Group Anagrams",
        "Given an array of strings strs, group the anagrams together. You can return the answer in any order. An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.",
        # correct: sort each word as key — O(n * k log k) where k = max string length
        "def groupAnagrams(strs):\n"
        "    groups = {}\n"
        "    for s in strs:\n"
        "        key = ''.join(sorted(s))\n"
        "        groups.setdefault(key, []).append(s)\n"
        "    return list(groups.values())",
        # partial: uses character count tuple as key — correct but more complex, O(n * k)
        "def groupAnagrams(strs):\n"
        "    groups = {}\n"
        "    for s in strs:\n"
        "        count = [0] * 26\n"
        "        for c in s:\n"
        "            count[ord(c) - ord('a')] += 1\n"
        "        groups.setdefault(tuple(count), []).append(s)\n"
        "    return list(groups.values())",
        # incorrect: groups by length instead of anagram
        "def groupAnagrams(strs):\n"
        "    groups = {}\n"
        "    for s in strs:\n"
        "        groups.setdefault(len(s), []).append(s)\n"
        "    return list(groups.values())",
    ),
]


def main():
    executor = TestExecutor()
    results = []

    for problem_name, problem_text, correct_code, partial_code, incorrect_code in PROBLEMS:
        for sol_type, code in [("correct", correct_code), ("partial", partial_code), ("incorrect", incorrect_code)]:
            case_id = f"{problem_name.replace(' ', '_')}_{sol_type}"

            try:
                ai = get_ai_verdict(problem_text, code)
            except Exception as e:
                ai = {
                    "model": "error",
                    "verdict": "incorrect",
                    "confidence": 0.5,
                    "reasoning": str(e),
                    "raw_response": str(e),
                }

            l2 = executor.verify(problem_name, code)

            edge_types = len(set(
                r.label.split('_')[0] for r in l2.results if not r.passed
            ))
            unique_patterns = len(set(str(r.label) for r in l2.results))

            ev = compute_evidence_strength(l2.total, edge_types, unique_patterns)
            label, flag = get_final_label(
                ai['verdict'], l2.pass_rate or 0, ev, ai['confidence']
            )

            # Rule 2: reasoning consistency check
            reasoning_ok = check_reasoning_matches_code(
                ai.get('reasoning', ''), code
            )

            # Risk computation — the core signal
            risk = compute_risk(ai['confidence'], ev)

            result = {
                "problem": case_id,
                "ground_truth": sol_type,
                "ai_verdict": ai['verdict'],
                "ai_confidence": ai['confidence'],
                "ai_reasoning": ai['reasoning'],
                "reasoning_matches_code": reasoning_ok,
                "evidence_strength": ev,
                "risk": risk['risk'],
                "risk_flagged": risk['flagged'],
                "execution_pass_rate": l2.pass_rate,
                "tests_total": l2.total,
                "final_label": label,
                "failure_flag": flag,
                "model": ai['model'],
            }
            results.append(result)
            print(f"{case_id}: risk={risk['risk']} flagged={risk['flagged']} | reasoning_ok={reasoning_ok} | ai={ai['verdict']}({ai['confidence']}) | ev={ev}")

    # Summary — only the two things that matter
    print(f"\n{'='*80}")
    print(f"SUMMARY: {len(results)} cases")

    # Measure 1: how many cases flagged by rule 1 (hard rule)
    rule1_flags = [r for r in results if r['failure_flag'] == 'FAIL:overconfident_on_weak_evidence']
    print(f"\nRule 1 — Overconfident on weak evidence: {len(rule1_flags)}/{len(results)} cases")
    for r in rule1_flags:
        print(f"  {r['problem']}: conf={r['ai_confidence']} ev={r['evidence_strength']} ai={r['ai_verdict']}")

    # Measure 2: how many cases fail the reasoning check
    reasoning_fails = [r for r in results if not r.get('reasoning_matches_code', True)]
    print(f"\nRule 2 — Reasoning doesn't match code: {len(reasoning_fails)}/{len(results)} cases")
    for r in reasoning_fails:
        print(f"  {r['problem']}: {r['ai_reasoning'][:120]}")

    # === RISK VALIDATION ===
    print(f"\n{'='*80}")
    print("RISK VALIDATION — risk = confidence × (1 − evidence)")

    # Correctness: ground_truth vs AI verdict
    for r in results:
        gt = r['ground_truth']
        av = r['ai_verdict']
        r['is_correct'] = (gt == av)

    # Per-risk-level breakdown
    print(f"\nPer risk level:")
    for bucket, label_name, lo, hi in [
        ("low risk",        "low",    0.0, 0.3),
        ("moderate risk",   "moderate", 0.3, 0.7),
        ("high risk",       "high",   0.7, 1.01),
    ]:
        cases = [r for r in results if lo <= r['risk'] < hi]
        if cases:
            n_correct = sum(1 for r in cases if r['is_correct'])
            avg_conf = sum(r['ai_confidence'] for r in cases) / len(cases)
            avg_ev = sum(r['evidence_strength'] for r in cases) / len(cases)
            print(f"  {bucket:15s}: {len(cases):2d} cases, {n_correct} correct ({n_correct/len(cases):.0%}), avg_conf={avg_conf:.2f}, avg_ev={avg_ev:.2f}")

    # Flagged cases
    flagged = [r for r in results if r['risk_flagged']]
    if flagged:
        print(f"\nFlagged (conf>=0.9, ev<0.4): {len(flagged)}/{len(results)} cases")
        for r in flagged:
            print(f"  {r['problem']}: risk={r['risk']} gt={r['ground_truth']} ai={r['ai_verdict']} correct={r['is_correct']}")

    out_path = r'F:\pythonProject\scratch\5_unseen_results.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == '__main__':
    main()
