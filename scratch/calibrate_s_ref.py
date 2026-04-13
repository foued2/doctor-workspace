import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'F:\pythonProject')
from doctor.test_executor import TestExecutor

problems = {
    'Two Sum': (
        "def twoSum(nums, target):\n"
        "    seen = {}\n"
        "    for i, n in enumerate(nums):\n"
        "        complement = target - n\n"
        "        if complement in seen:\n"
        "            return [seen[complement], i]\n"
        "        seen[n] = i\n"
        "    return []"
    ),
    'Valid Parentheses': (
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
    'N-Queens': (
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
    'Container With Most Water': (
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
    'Trapping Rain Water': (
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
}

executor = TestExecutor()
print("S_REF CALIBRATION — Measuring canonical solution times")
print("=" * 70)

for prob_name, code in problems.items():
    report = executor.verify(prob_name, code)
    total_ms = sum(t.get('execution_time', 0.0) * 1000 for t in report.traces)
    print(f"  {prob_name:<30s}: total_ms={total_ms:.4f}  "
          f"tests={len(report.traces)}  verdict={report.verdict}")
    for i, t in enumerate(report.traces):
        ms = t.get('execution_time', 0) * 1000
        print(f"    test {i}: {ms:.4f}ms  passed={t.get('passed')}")
