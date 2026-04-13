"""Audit N-Queens_partial L2 behavior."""
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
    if r.got:
        print(f"    Got {len(r.got)} solution(s):")
        for sol in r.got[:2]:
            print(f"      {sol}")
    if r.expected:
        print(f"    Expected {len(r.expected)} solution(s):")
        for sol in r.expected[:2]:
            print(f"      {sol}")
    print()

# Now check: are the solutions the partial found VALID?
# And are they a subset of the expected solutions?
print("Checking subset validity...")
# For n=4, there are 2 valid solutions. Partial finds 1.
# That 1 should be a subset of the 2 expected solutions.
