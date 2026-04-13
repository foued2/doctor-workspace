"""
V/C Enumeration Evaluator — N-Queens only.

Two-signal model:
  V (validity)    = how much of the produced output is actually correct
  C (completeness) = how much of the required output space is covered

Classification:
  correct   → V == 1 AND C == 1
  partial   → V > 0 AND (V < 1 OR C < 1)
  incorrect → V == 0

Scope: N-Queens enumeration problems only. No system changes.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'F:\pythonProject')


# ============================================================
# Step 1 — Concrete metric definitions for N-Queens
# ============================================================

def is_valid_board(board: list[str], n: int) -> bool:
    """Check if a single board representation is a valid N-Queens solution.

    Board is a list of n strings, each of length n, with exactly one 'Q' per row.

    Validates:
    - Exactly n rows
    - Each row has exactly one 'Q'
    - No two queens share a column
    - No two queens share a diagonal
    """
    if not isinstance(board, list):
        return False
    if len(board) != n:
        return False

    queen_cols = []
    for row_idx, row in enumerate(board):
        if not isinstance(row, str):
            return False
        if len(row) != n:
            return False
        q_positions = [i for i, ch in enumerate(row) if ch == 'Q']
        if len(q_positions) != 1:
            return False
        col = q_positions[0]
        # Check column conflict
        if col in queen_cols:
            return False
        # Check diagonal conflicts
        for prev_row, prev_col in enumerate(queen_cols):
            if abs(col - prev_col) == abs(row_idx - prev_row):
                return False
        queen_cols.append(col)
    return True


def count_known_solutions(n: int) -> int:
    """Return the known number of distinct N-Queens solutions for board size n."""
    # OEIS A000170
    known = {0: 1, 1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92,
             9: 352, 10: 724}
    return known.get(n, None)


def evaluate_vc(solutions_pred: list, n: int) -> dict:
    """Evaluate a predicted solution list using V/C metrics.

    Returns:
        dict with V, C, valid_count, invalid_count, total_pred, expected_count,
        classification, and raw details.
    """
    total_pred = len(solutions_pred)
    expected_count = count_known_solutions(n)

    if total_pred == 0:
        return {
            "V": 0.0,
            "C": 0.0,
            "valid_count": 0,
            "invalid_count": 0,
            "duplicate_count": 0,
            "total_pred": 0,
            "expected_count": expected_count,
            "classification": "incorrect",
            "boards_valid": [],
            "boards_invalid": [],
        }

    valid_boards = []
    invalid_boards = []
    seen = set()
    duplicate_count = 0

    for board in solutions_pred:
        board_key = tuple(board) if isinstance(board, list) else None
        if board_key in seen:
            duplicate_count += 1
            continue
        seen.add(board_key)

        if is_valid_board(board, n):
            valid_boards.append(board)
        else:
            invalid_boards.append(board)

    valid_count = len(valid_boards)
    invalid_count = len(invalid_boards)

    # V = fraction of UNIQUE predicted outputs that are valid
    unique_total = valid_count + invalid_count
    V = valid_count / unique_total if unique_total > 0 else 0.0

    # C = fraction of expected solution space covered
    C = valid_count / expected_count if expected_count and expected_count > 0 else 0.0

    # Classification
    if valid_count == 0:
        classification = "incorrect"
    elif valid_count == expected_count and invalid_count == 0:
        classification = "correct"
    else:
        classification = "partial"

    return {
        "V": round(V, 4),
        "C": round(C, 4),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "duplicate_count": duplicate_count,
        "total_pred": total_pred,
        "expected_count": expected_count,
        "classification": classification,
        "boards_valid": valid_boards,
        "boards_invalid": invalid_boards,
    }


# ============================================================
# Step 3 — Test cases: three N-Queens solutions (n=4)
# ============================================================

SOLUTIONS_N4 = {
    # Backtracking with full enumeration — all 2 solutions
    "correct": (
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
    # Backtracking stops at first solution — returns 1 of 2
    "partial": (
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
    # Permutation approach — no diagonal check (returns ALL permutations = invalid)
    "incorrect": (
        "def solveNQueens(n):\n"
        "    from itertools import permutations\n"
        "    results = []\n"
        "    for perm in permutations(range(n)):\n"
        "        board = [['.'] * n for _ in range(n)]\n"
        "        for r, c in enumerate(perm):\n"
        "            board[r][c] = 'Q'\n"
        "        results.append([''.join(r) for r in board])\n"
        "    return results"
    ),
}

N = 4

print("=" * 70)
print(f"V/C ENUMERATION EVALUATOR — N-Queens (n={N})")
print("=" * 70)

# Execute each solution and evaluate with V/C
for label, code in SOLUTIONS_N4.items():
    namespace = {}
    exec(code, namespace)
    func = namespace["solveNQueens"]
    raw_output = func(N)

    result = evaluate_vc(raw_output, N)

    print(f"\n{'─' * 70}")
    print(f"  Case: {label.upper()}")
    print(f"{'─' * 70}")
    print(f"  V (validity):     {result['V']}")
    print(f"  C (completeness): {result['C']}")
    print(f"  Classification:   {result['classification']}")
    print(f"")
    print(f"  Raw outputs:")
    print(f"    Total predicted:    {result['total_pred']}")
    print(f"    Valid unique:       {result['valid_count']}")
    print(f"    Invalid unique:     {result['invalid_count']}")
    print(f"    Duplicates:         {result['duplicate_count']}")
    print(f"    Expected:           {result['expected_count']}")
    print(f"")
    if result['boards_valid']:
        print(f"  Valid boards ({len(result['boards_valid'])}):")
        for i, board in enumerate(result['boards_valid'][:3]):
            for row in board:
                print(f"    {row}")
            print()
        if len(result['boards_valid']) > 3:
            print(f"    ... and {len(result['boards_valid']) - 3} more")
    if result['boards_invalid']:
        print(f"  Invalid boards ({len(result['boards_invalid'])}):")
        for i, board in enumerate(result['boards_invalid'][:2]):
            for row in board:
                print(f"    {row}")
            print()
        if len(result['boards_invalid']) > 2:
            print(f"    ... and {len(result['boards_invalid']) - 2} more")

# ============================================================
# Step 4 — Additional edge-case tests
# ============================================================

print(f"\n{'=' * 70}")
print(f"  EDGE-CASE TESTS")
print(f"{'=' * 70}")

edge_cases = {
    "empty_output": {
        "output": [],
        "desc": "Returns nothing / empty list",
    },
    "duplicate_boards": {
        "output": [
            [".Q..", "...Q", "Q...", "..Q."],
            [".Q..", "...Q", "Q...", "..Q."],  # duplicate
        ],
        "desc": "Returns same valid board twice",
    },
    "mix_valid_invalid": {
        "output": [
            [".Q..", "...Q", "Q...", "..Q."],   # valid
            ["Q...", "...Q", ".Q..", "..Q."],   # invalid (diagonal)
            ["....", "....", "....", "...."],   # invalid (no queens)
        ],
        "desc": "1 valid + 2 invalid boards",
    },
    "all_invalid": {
        "output": [
            ["Q...", ".Q..", "..Q.", "...Q"],   # invalid (diagonal)
            ["....", "....", "....", "...."],   # invalid (empty)
        ],
        "desc": "No valid boards at all",
    },
    "only_duplicates": {
        "output": [
            [".Q..", "...Q", "Q...", "..Q."],
            [".Q..", "...Q", "Q...", "..Q."],
            [".Q..", "...Q", "Q...", "..Q."],
        ],
        "desc": "Same valid board 3 times (n=4 expects 2)",
    },
}

for case_id, case in edge_cases.items():
    result = evaluate_vc(case["output"], N)
    print(f"\n  ── {case_id}: {case['desc']} ──")
    print(f"    V={result['V']}, C={result['C']}, classification={result['classification']}")
    print(f"    valid={result['valid_count']}, invalid={result['invalid_count']}, "
          f"duplicates={result['duplicate_count']}")


# ============================================================
# Step 4 — Limitations report
# ============================================================

print(f"\n{'=' * 70}")
print(f"  LIMITATIONS REPORT")
print(f"{'=' * 70}")

limitations = [
    ("Duplicate boards",
     "Duplicates are de-duplicated before counting. V/C reflect UNIQUE "
     "boards only. This is correct behavior — duplicates don't increase "
     "validity or completeness. A solution returning the same board 100x "
     "gets V=1.0 but C=1/n (only 1 unique valid out of n expected)."),

    ("Mix of valid + invalid boards",
     "V penalizes the fraction that is invalid. If output has 1 valid + "
     "2 invalid → V = 1/3 = 0.333. C reflects only the valid ones. "
     "Invalid boards actively hurt V, they don't just fail to help C."),

    ("Generalization to other enumeration problems",
     "V/C generalizes to any problem where: "
     "(1) There is a known finite solution space (expected_count), "
     "(2) Each output can be independently validated, "
     "(3) Duplicates can be detected and removed. "
     "Examples: Generate Parentheses, 3Sum, Letter Combinations. "
     "Does NOT generalize to: optimization problems (single-answer), "
     "decision problems (yes/no), or infinite-solution problems."),

    ("Known solution count dependency",
     "C requires knowing the exact expected_count. For N-Queens this is "
     "from OEIS A000170. For other enumeration problems, we need either "
     "a reference implementation or a pre-computed answer key. This is "
     "a practical limitation — not all problems have known counts."),

    ("Validation function dependency",
     "V requires is_valid_board() — a problem-specific validator. "
     "Each new enumeration problem needs its own validator. This is "
     "not a flaw but a structural requirement of the V/C model."),

    ("Order independence",
     "V/C is order-independent by design. Solutions returned in any "
     "order get the same V/C score. This matches the problem spec "
     "('return all distinct solutions') where order doesn't matter."),
]

for title, text in limitations:
    print(f"\n  [{title}]")
    print(f"    {text}")
