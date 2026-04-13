"""Verify N-Queens partial with new n4_finds_one test."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'F:\pythonProject')

from doctor.test_executor import TestExecutor

partial_code = (
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
)

executor = TestExecutor()
report = executor.verify("N-Queens", partial_code)

print(f"Verdict: {report.verdict}")
print(f"Pass rate: {report.pass_rate} ({report.passed}/{report.total})")
print()
for r in report.results:
    print(f"  {r.label:20s} pass={r.passed}")
print()

# Also check correct and incorrect solutions
correct_code = (
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
)

report2 = executor.verify("N-Queens", correct_code)
print(f"Correct — Verdict: {report2.verdict}, Pass rate: {report2.pass_rate} ({report2.passed}/{report2.total})")
for r in report2.results:
    print(f"  {r.label:20s} pass={r.passed}")
print()

incorrect_code = (
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
)

report3 = executor.verify("N-Queens", incorrect_code)
print(f"Incorrect (perm) — Verdict: {report3.verdict}, Pass rate: {report3.pass_rate} ({report3.passed}/{report3.total})")
for r in report3.results:
    print(f"  {r.label:20s} pass={r.passed}")
