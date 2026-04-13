"""
S-Scaling Experiment — Multi-Point Growth Analysis
=====================================================
Replace single-point S with a growth signature across ≥3 input sizes.

For each non-linear problem:
  1. Define input ladder: n1, n2, n3 where n_{k+1} ≈ 2*n_k
  2. Run canonical + brute solutions at each size
  3. Compute S_observed(n) for each
  4. Derive growth indicators:
     - ratio: S(n2)/S(n1), S(n3)/S(n2)
     - log-slope: fit line to log(S) vs log(n)
  5. Classify:
     - efficient: sub-quadratic growth (slope < ~2)
     - inefficient: super-polynomial/exponential (slope > ~3)
     - ambiguous: insufficient separation

This captures the asymptotic behavior, not a single-point snapshot.
"""

import sys
import json
import time
import copy
sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
# TRACE (same as run_s_final.py)
# ═══════════════════════════════════════════════════════════

class Trace:
    def __init__(self):
        self.steps = 0
        self.unique = set()
        self.solutions = 0
        self.start_time = time.perf_counter()
        self.elapsed_ms = 0.0

    def record(self, key):
        self.steps += 1
        self.unique.add(str(key))

    def record_solution(self):
        self.solutions += 1

    def stop(self):
        self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0


# ═══════════════════════════════════════════════════════════
# N-QUEENS SOLVERS (instrumented)
# ═══════════════════════════════════════════════════════════

def is_valid_nq(board, row, col):
    for r in range(row):
        if board[r] == col or abs(board[r] - col) == abs(r - row):
            return False
    return True

def nq_correct(n, t):
    """Backtracking with pruning — O(n!) but pruned."""
    sols = []
    def bt(row, board):
        t.record(('call', row, tuple(board)))
        if row == n:
            sols.append(board[:]); t.record_solution(); return
        for col in range(n):
            if is_valid_nq(board, row, col):
                board[row] = col; t.record(('place', row, col))
                bt(row+1, board)
                board[row] = -1
    bt(0, [-1]*n)
    return sols

def nq_bruteforce(n, t):
    """Generate all permutations and validate — O(n! * n^2)."""
    sols = []
    def gen(row, board):
        if row == n:
            t.record(('validate', tuple(board)))
            valid = all(
                board[i] != board[j] and abs(board[i]-board[j]) != abs(i-j)
                for i in range(n) for j in range(i)
            )
            if valid: sols.append(board[:]); t.record_solution()
            return
        for col in range(n):
            board[row] = col; t.record(('assign', row, col))
            gen(row+1, board); board[row] = -1
    gen(0, [-1]*n)
    return sols

def nq_partial(n, t):
    """Find first solution only — backtracking stops early."""
    sols = []
    def bt(row, board):
        t.record(('call', row, tuple(board)))
        if row == n:
            sols.append(board[:]); t.record_solution(); return True
        for col in range(n):
            if is_valid_nq(board, row, col):
                board[row] = col; t.record(('place', row, col))
                if bt(row+1, board): return True
                board[row] = -1
    bt(0, [-1]*n)
    return sols


# ═══════════════════════════════════════════════════════════
# SUDOKU SOLVERS (instrumented)
# ═══════════════════════════════════════════════════════════

def poss(board, r, c):
    filled = {board[r][k] for k in range(9) if board[r][k] != '.'}
    filled |= {board[k][c] for k in range(9) if board[k][c] != '.'}
    br, bc = 3*(r//3), 3*(c//3)
    for rr in range(br, br+3):
        for cc in range(bc, bc+3):
            if board[rr][cc] != '.': filled.add(board[rr][cc])
    return [d for d in "123456789" if d not in filled]

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == '.': return (i,j)
    return None

def sudoku_correct(board, t):
    b = copy.deepcopy(board)
    def solve():
        e = find_empty(b)
        if e is None: t.record(('solved',)); t.record_solution(); return True
        r, c = e; p = poss(b, r, c); t.record(('cell', r, c, len(p)))
        for d in p:
            b[r][c] = d; t.record(('try', r, c, d))
            if solve(): return True
            b[r][c] = '.'; t.record(('backtrack', r, c))
        return False
    solve(); return b

def sudoku_bruteforce(board, t):
    """Brute: try all combinations for first K empty cells."""
    b = copy.deepcopy(board)
    empties = [(i,j) for i in range(9) for j in range(9) if b[i][j]=='.']
    K = min(len(empties), 6)  # cap for feasibility
    def go(idx):
        if idx == K:
            t.record(('validate',))
            return
        r, c = empties[idx]
        for d in "123456789":
            b[r][c] = d; t.record(('assign', r, c, d, idx))
            go(idx+1)
        b[r][c] = '.'
    go(0); return b


# ═══════════════════════════════════════════════════════════
# GROWTH ANALYSIS
# ═══════════════════════════════════════════════════════════

def compute_growth(sizes, observed_values):
    """Compute growth signature from multi-point measurements.

    Args:
        sizes: list of input sizes [n1, n2, n3, ...]
        observed_values: list of S_observed (step counts) at each size

    Returns:
        dict with growth indicators
    """
    if len(sizes) < 2 or len(observed_values) < 2:
        return {"status": "insufficient_data"}

    # Compute ratios between consecutive points
    ratios = []
    for i in range(1, len(sizes)):
        if observed_values[i-1] > 0:
            ratio = observed_values[i] / observed_values[i-1]
            size_ratio = sizes[i] / sizes[i-1]
            ratios.append({
                "size_from": sizes[i-1],
                "size_to": sizes[i],
                "size_ratio": round(size_ratio, 2),
                "obs_ratio": round(ratio, 2),
                "empirical_exponent": round(
                    _log_ratio(observed_values[i], observed_values[i-1]), 2
                ) if observed_values[i-1] > 0 else None,
            })

    # Fit log-log slope (linear regression on log-transformed data)
    log_sizes = [_safe_log(s) for s in sizes]
    log_obs = [_safe_log(o) for o in observed_values if o > 0]
    # Align: drop sizes where obs <= 0
    aligned = [(s, o) for s, o in zip(sizes, observed_values) if o > 0]
    if len(aligned) >= 2:
        log_s = [_safe_log(s) for s, _ in aligned]
        log_o = [_safe_log(o) for _, o in aligned]
        slope, intercept = _linear_fit(log_s, log_o)
    else:
        slope = None
        intercept = None

    return {
        "status": "ok",
        "ratios": ratios,
        "log_log_slope": round(slope, 3) if slope is not None else None,
        "interpretation": _interpret_slope(slope),
    }


def _safe_log(x):
    import math
    return math.log(x) if x > 0 else 0.0

def _log_ratio(a, b):
    import math
    if a <= 0 or b <= 0 or a == b:
        return 0.0
    return math.log(a / b) / math.log(2) if b != 1 else 0.0

def _linear_fit(xs, ys):
    """Simple least-squares fit: y = slope * x + intercept."""
    n = len(xs)
    if n < 2:
        return 0.0, 0.0
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xy = sum(x * y for x, y in zip(xs, ys))
    sum_x2 = sum(x * x for x in xs)
    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        return 0.0, sum_y / n
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept

def _interpret_slope(slope):
    """Classify based on log-log slope."""
    if slope is None:
        return "ambiguous"
    if slope < 2.0:
        return "efficient"       # sub-quadratic
    elif slope < 4.0:
        return "moderate"        # quadratic to moderate polynomial
    else:
        return "inefficient"     # super-polynomial / exponential


# ═══════════════════════════════════════════════════════════
# EXPERIMENT
# ═══════════════════════════════════════════════════════════

def run():
    all_results = {}

    # ─── N-Queens: Input Ladder ───
    print("=" * 90)
    print("N-QUEENS — Multi-Point Scaling")
    print("=" * 90)
    nq_sizes = [4, 6, 8]  # n, 1.5n, 2n
    nq_experiments = {
        'correct':    nq_correct,
        'partial':    nq_partial,
        'bruteforce': nq_bruteforce,
    }

    for regime_name, solver in nq_experiments.items():
        print(f"\n  --- {regime_name} ---")
        nq_observed = []
        nq_times = []

        for n in nq_sizes:
            t = Trace()
            try:
                solver(n, t)
                t.stop()
                s_obs = t.steps
                elapsed = t.elapsed_ms
                nq_observed.append(s_obs)
                nq_times.append(elapsed)
                print(f"    n={n:>2d}: S_obs={s_obs:>10,}  "
                      f"time={elapsed:.3f}ms  sols={t.solutions}  "
                      f"unique={len(t.unique)}")
            except Exception as e:
                print(f"    n={n:>2d}: ERROR — {e}")
                nq_observed.append(0)
                nq_times.append(0)

        growth = compute_growth(nq_sizes, nq_observed)
        growth_time = compute_growth(nq_sizes, nq_times)

        all_results[f'N-Queens_{regime_name}'] = {
            'sizes': nq_sizes,
            's_observed': nq_observed,
            's_time_ms': [round(t, 4) for t in nq_times],
            'growth_steps': growth,
            'growth_time': growth_time,
        }

        print(f"    Growth (steps): {growth['interpretation']}  "
              f"log-log slope={growth.get('log_log_slope', 'N/A')}")
        if growth.get('ratios'):
            for r in growth['ratios']:
                print(f"      n={r['size_from']}→{r['size_to']}: "
                      f"size_x{r['size_ratio']}  obs_x{r['obs_ratio']}  "
                      f"exponent={r['empirical_exponent']}")

    # ─── Sudoku: Vary number of empty cells ───
    print(f"\n{'='*90}")
    print(f"SUDOKU — Multi-Point Scaling (varying empty cells)")
    print(f"{'='*90}")

    # Create Sudoku boards with different numbers of empty cells
    def make_sudoku(empty_count):
        """Start from empty board and fill empty_count cells."""
        board = [['.' for _ in range(9)] for _ in range(9)]
        # Fill some known cells to make it solvable
        known = [
            (0,0,'5'),(0,1,'3'),(0,4,'7'),
            (1,0,'6'),(1,3,'1'),(1,4,'9'),(1,5,'5'),
            (2,1,'9'),(2,2,'8'),(2,8,'6'),
            (3,0,'8'),(3,4,'6'),(3,8,'3'),
            (4,0,'4'),(4,3,'8'),(4,5,'3'),(4,8,'1'),
            (5,0,'7'),(5,4,'2'),(5,8,'6'),
            (6,1,'6'),(6,6,'2'),(6,7,'8'),
            (7,3,'4'),(7,4,'1'),(7,5,'9'),(7,8,'5'),
            (8,4,'8'),(8,7,'7'),(8,8,'9'),
        ]
        # Use the standard Sudoku board
        std = [
            ["5","3",".",".","7",".",".",".","."],
            ["6",".",".","1","9","5",".",".","."],
            [".","9","8",".",".",".",".","6","."],
            ["8",".",".",".","6",".",".",".","3"],
            ["4",".",".","8",".","3",".",".","1"],
            ["7",".",".",".","2",".",".",".","6"],
            [".","6",".",".",".",".","2","8","."],
            [".",".",".","4","1","9",".",".","5"],
            [".",".",".",".","8",".",".","7","9"],
        ]
        # Adjust empty count by converting some cells to '.'
        filled_cells = [(i,j) for i in range(9) for j in range(9) if std[i][j] != '.']
        target_empty = empty_count
        current_filled = 81 - sum(row.count('.') for row in std)  # 30 filled
        current_empty = 81 - current_filled  # 51 empty

        if target_empty < current_empty:
            # Fill in some empty cells (from our filled_cells list)
            import random
            random.seed(42)
            to_fill = current_empty - target_empty
            # Pick some empty cells and fill them (from known standard solution)
            solution = [
                ["5","3","4","6","7","8","9","1","2"],
                ["6","7","2","1","9","5","3","4","8"],
                ["1","9","8","3","4","2","5","6","7"],
                ["8","5","9","7","6","1","4","2","3"],
                ["4","2","6","8","5","3","7","9","1"],
                ["7","1","3","9","2","4","8","5","6"],
                ["9","6","1","5","3","7","2","8","4"],
                ["2","8","7","4","1","9","6","3","5"],
                ["3","4","5","2","8","6","1","7","9"],
            ]
            empty_cells = [(i,j) for i in range(9) for j in range(9) if std[i][j] == '.']
            random.shuffle(empty_cells)
            for i, j in empty_cells[:to_fill]:
                std[i][j] = solution[i][j]
        elif target_empty > current_empty:
            # Remove some filled cells
            import random
            random.seed(42)
            to_remove = target_empty - current_empty
            filled = [(i,j) for i in range(9) for j in range(9) if std[i][j] != '.']
            random.shuffle(filled)
            for i, j in filled[:to_remove]:
                std[i][j] = '.'

        return std

    # Sudoku sizes: different numbers of empty cells
    sd_sizes = [30, 40, 51]  # empty cells
    sd_experiments = {
        'correct': lambda b, t: sudoku_correct(b, t),
        'bruteforce': lambda b, t: sudoku_bruteforce(b, t),
    }

    for regime_name, solver in sd_experiments.items():
        print(f"\n  --- {regime_name} ---")
        sd_observed = []
        sd_times = []

        for empty_count in sd_sizes:
            board = make_sudoku(empty_count)
            t = Trace()
            try:
                solver(copy.deepcopy(board), t)
                t.stop()
                s_obs = t.steps
                elapsed = t.elapsed_ms
                sd_observed.append(s_obs)
                sd_times.append(elapsed)
                print(f"    empty={empty_count:>2d}: S_obs={s_obs:>10,}  "
                      f"time={elapsed:.3f}ms  sols={t.solutions}")
            except Exception as e:
                print(f"    empty={empty_count:>2d}: ERROR — {e}")
                sd_observed.append(0)
                sd_times.append(0)

        growth = compute_growth(sd_sizes, sd_observed)
        growth_time = compute_growth(sd_sizes, sd_times)

        all_results[f'Sudoku_{regime_name}'] = {
            'sizes': sd_sizes,
            's_observed': sd_observed,
            's_time_ms': [round(t, 4) for t in sd_times],
            'growth_steps': growth,
            'growth_time': growth_time,
        }

        print(f"    Growth (steps): {growth['interpretation']}  "
              f"log-log slope={growth.get('log_log_slope', 'N/A')}")
        if growth.get('ratios'):
            for r in growth['ratios']:
                print(f"      empty={r['size_from']}→{r['size_to']}: "
                      f"size_x{r['size_ratio']}  obs_x{r['obs_ratio']}  "
                      f"exponent={r['empirical_exponent']}")

    # ═══════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════

    print(f"\n{'='*90}")
    print(f"SCALING SUMMARY")
    print(f"{'='*90}")
    print(f"  {'Experiment':<25s} | {'Slope':>8s} | {'Class':<15s} | {'Sizes':<15s}")
    print(f"  {'-'*25}-+-{'-'*8}-+-{'-'*15}-+-{'-'*15}")

    for exp_name, data in all_results.items():
        gs = data.get('growth_steps', {})
        slope = gs.get('log_log_slope', 'N/A')
        interp = gs.get('interpretation', 'N/A')
        sizes = data.get('sizes', [])
        slope_str = f"{slope:.2f}" if isinstance(slope, (int, float)) else str(slope)
        sizes_str = str(sizes)
        print(f"  {exp_name:<25s} | {slope_str:>8s} | {interp:<15s} | {sizes_str:<15s}")

    # Save
    path = r'F:\pythonProject\scratch\s_scaling_results.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved: {path}")


if __name__ == '__main__':
    run()
