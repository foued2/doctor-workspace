"""
S-DIMENSION CROSS-PROBLEM VALIDATION
=====================================
Hypothesis: curvature of execution growth curves separates
  brute force vs correct backtracking vs partial solutions
  ACROSS problem domains.

Problems:
  1. N-Queens (n=6)
  2. Word Search
  3. Sudoku Solver

For each problem, run 3 regimes:
  - correct (full backtracking, finds all solutions)
  - partial (backtracking, stops at first solution)
  - brute-force (exhaustive enumeration)

Measures:
  S(t) = cumulative states at decision step t
  curvature = second-order growth behavior
  total_work = total calls (optional reference)

Acceptance: curvature boundaries stable across all 3 problems.
"""

import copy
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
# GROWTH TRACE — shared instrumentation
# ═══════════════════════════════════════════════════════════

class GrowthTrace:
    """
    Tracks execution as a sequence of decision steps.
    t = step index (sequential decision point, not recursive depth)
    
    S(t) = cumulative unique states explored up to step t
    curvature = second derivative of S(t)
    """
    def __init__(self):
        self.step_states = []   # list of (step, state_key) 
        self.step_count = 0
        self.solutions_found = 0
        self.state_seen = {}    # state_key -> count
        
    def record(self, step_hint, state_key):
        """Record a state exploration at a decision step."""
        self.step_count += 1
        key = str(state_key)
        self.state_seen[key] = self.state_seen.get(key, 0) + 1
        self.step_states.append((self.step_count, key, step_hint))
    
    def record_solution(self):
        self.solutions_found += 1
    
    def compute_growth_curve(self):
        """
        Compute S(t) = cumulative unique states up to step t.
        Returns list of dicts for each step.
        """
        curve = []
        cum_unique = 0
        unique_so_far = set()
        
        for step, state_key, hint in self.step_states:
            if state_key not in unique_so_far:
                unique_so_far.add(state_key)
                cum_unique += 1
            curve.append({
                'step': step,
                'cumulative_unique': cum_unique,
                'hint': hint,
            })
        
        return curve
    
    def compute_curvature(self):
        """
        Estimate curvature from the growth curve.
        Uses quadratic fit: S(t) ≈ a*t² + b*t + c
        curvature = 2*a (coefficient of t²)
        
        Returns:
          curvature: positive = accelerating, negative = decelerating, ~0 = linear
          r_squared: how well quadratic fits (confidence in curvature estimate)
        """
        curve = self.compute_growth_curve()
        n = len(curve)
        if n < 3:
            return {'curvature': 0, 'r_squared': 0, 'n_points': n}
        
        # Subsample for large curves (take evenly spaced points)
        MAX_POINTS = 200
        if n > MAX_POINTS:
            indices = [int(i * n / MAX_POINTS) for i in range(MAX_POINTS)]
            sampled = [curve[i] for i in indices]
        else:
            sampled = curve
        
        # Normalize t to [0, 1] for numerical stability
        t_max = sampled[-1]['step']
        s_max = sampled[-1]['cumulative_unique']
        
        if t_max == 0 or s_max == 0:
            return {'curvature': 0, 'r_squared': 0, 'n_points': len(sampled)}
        
        ts = [c['step'] / t_max for c in sampled]
        ss = [c['cumulative_unique'] / s_max for c in sampled]
        
        # Fit quadratic: s = a*t² + b*t + c via least squares
        # Normal equations: [Σt⁴  Σt³  Σt²] [a]   [Σt²s]
        #                   [Σt³  Σt²  Σt ] [b] = [Σts ]
        #                   [Σt²  Σt   n  ] [c]   [Σs  ]
        sum_t = sum(ts)
        sum_t2 = sum(t*t for t in ts)
        sum_t3 = sum(t*t*t for t in ts)
        sum_t4 = sum(t*t*t*t for t in ts)
        sum_s = sum(ss)
        sum_ts = sum(t*s for t, s in zip(ts, ss))
        sum_t2s = sum(t*t*s for t, s in zip(ts, ss))
        m = len(sampled)
        
        # 3x3 matrix solve (Cramer's rule)
        # | sum_t4  sum_t3  sum_t2 | |a|   |sum_t2s|
        # | sum_t3  sum_t2  sum_t  | |b| = |sum_ts |
        # | sum_t2  sum_t   m      | |c|   |sum_s  |
        
        det = (sum_t4 * (sum_t2 * m - sum_t * sum_t)
             - sum_t3 * (sum_t3 * m - sum_t * sum_t2)
             + sum_t2 * (sum_t3 * sum_t - sum_t2 * sum_t2))
        
        if abs(det) < 1e-15:
            return {'curvature': 0, 'r_squared': 0, 'n_points': len(sampled)}
        
        a = (sum_t2s * (sum_t2 * m - sum_t * sum_t)
           - sum_t3 * (sum_ts * m - sum_t * sum_s)
           + sum_t2 * (sum_ts * sum_t - sum_t2 * sum_s)) / det
        
        # R²: 1 - SS_res / SS_tot
        predicted = [a*t*t + 0*t + 0 for t in ts]  # simplified; compute properly
        # Actually compute full fit:
        # Need b and c too for proper R²
        b = (sum_t4 * (sum_ts * m - sum_t * sum_s)
           - sum_t2s * (sum_t3 * m - sum_t * sum_t2)
           + sum_t2 * (sum_t3 * sum_s - sum_ts * sum_t2)) / det
        c = (sum_t4 * (sum_t2 * sum_s - sum_t * sum_ts)
           - sum_t3 * (sum_t3 * sum_s - sum_t * sum_t2s)
           + sum_t2s * (sum_t3 * sum_t - sum_t2 * sum_t2)) / det
        
        predicted = [a*t*t + b*t + c for t in ts]
        ss_res = sum((s - p)**2 for s, p in zip(ss, predicted))
        s_mean = sum_s / m
        ss_tot = sum((s - s_mean)**2 for s in ss)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        
        # curvature = 2*a (since S(t) = a*t² + b*t + c, second derivative = 2a)
        # But we normalized t and s, so scale back:
        # a_raw = a * s_max / (t_max**2)
        curvature_raw = 2 * a * s_max / (t_max ** 2) if t_max > 0 else 0
        
        return {
            'curvature': round(curvature_raw, 6),
            'r_squared': round(r_squared, 4),
            'n_points': len(sampled),
            'coeff_a': round(a, 6),
            'coeff_b': round(b, 6),
            'coeff_c': round(c, 6),
        }


# ═══════════════════════════════════════════════════════════
# PROBLEM 1: N-QUEENS (n=6)
# ═══════════════════════════════════════════════════════════

def is_valid_nqueens(board, row, col):
    for r in range(row):
        c = board[r]
        if c == col or abs(c - col) == abs(r - row):
            return False
    return True

def nqueens_correct(n, trace):
    """Correct backtracking: finds ALL solutions."""
    solutions = []
    def backtrack(row, board):
        trace.record(row, ('call', row, tuple(board)))
        if row == n:
            solutions.append(copy.deepcopy(board))
            trace.record_solution()
            return
        for col in range(n):
            if is_valid_nqueens(board, row, col):
                board[row] = col
                trace.record(row, ('place', row, col, tuple(board)))
                backtrack(row + 1, board)
                board[row] = -1
                trace.record(row, ('unplace', row, tuple(board)))
    backtrack(0, [-1] * n)
    return solutions

def nqueens_partial(n, trace):
    """Partial backtracking: finds FIRST solution then stops."""
    solutions = []
    def backtrack(row, board):
        trace.record(row, ('call', row, tuple(board)))
        if row == n:
            solutions.append(copy.deepcopy(board))
            trace.record_solution()
            return True
        for col in range(n):
            if is_valid_nqueens(board, row, col):
                board[row] = col
                trace.record(row, ('place', row, col, tuple(board)))
                if backtrack(row + 1, board):
                    return True
                board[row] = -1
                trace.record(row, ('unplace', row, tuple(board)))
    backtrack(0, [-1] * n)
    return solutions

def nqueens_bruteforce(n, trace):
    """Brute force: enumerates all n^n candidates, validates each."""
    solutions = []
    def generate(row, board):
        if row == n:
            trace.record(row, ('validate', tuple(board)))
            valid = True
            for i in range(n):
                for j in range(i):
                    if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                        valid = False
                        break
                    trace.record(row, ('check', i, j))
            if valid:
                solutions.append(copy.deepcopy(board))
                trace.record_solution()
            return
        for col in range(n):
            board[row] = col
            trace.record(row, ('assign', row, col))
            generate(row + 1, board)
            board[row] = -1
    generate(0, [-1] * n)
    return solutions


# ═══════════════════════════════════════════════════════════
# PROBLEM 2: WORD SEARCH
# ═══════════════════════════════════════════════════════════

WS_BOARD = [
    ['A', 'B', 'C', 'E'],
    ['S', 'F', 'C', 'S'],
    ['A', 'D', 'E', 'E']
]
WS_WORD = "ABCCED"  # exists: True

def word_search_correct(board, word, trace):
    """Correct backtracking DFS: finds if word exists."""
    rows, cols = len(board), len(board[0])
    
    def dfs(r, c, i):
        trace.record(i, ('dfs', r, c, i, board[r][c] if 0 <= r < rows and 0 <= c < cols else 'OOB'))
        if i == len(word):
            trace.record_solution()
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return False
        if board[r][c] != word[i]:
            return False
        
        tmp = board[r][c]
        board[r][c] = '#'
        trace.record(i, ('mark', r, c))
        
        found = (dfs(r+1, c, i+1) or dfs(r-1, c, i+1) or
                 dfs(r, c+1, i+1) or dfs(r, c-1, i+1))
        
        board[r][c] = tmp
        trace.record(i, ('unmark', r, c))
        return found
    
    for r in range(rows):
        for c in range(cols):
            trace.record(0, ('start', r, c))
            if dfs(r, c, 0):
                return True
    return False

def word_search_partial(board, word, trace):
    """Partial: same as correct but stops at first match (identical behavior for boolean return).
    The difference is in the search order — we simulate partial by limiting starting cells."""
    rows, cols = len(board), len(board[0])
    
    def dfs(r, c, i):
        trace.record(i, ('dfs', r, c, i, board[r][c] if 0 <= r < rows and 0 <= c < cols else 'OOB'))
        if i == len(word):
            trace.record_solution()
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return False
        if board[r][c] != word[i]:
            return False
        
        tmp = board[r][c]
        board[r][c] = '#'
        trace.record(i, ('mark', r, c))
        
        # Only try 2 directions instead of 4 (simulating incomplete exploration)
        found = (dfs(r+1, c, i+1) or dfs(r, c+1, i+1))
        
        board[r][c] = tmp
        trace.record(i, ('unmark', r, c))
        return found
    
    # Only start from first row (partial coverage)
    for c in range(cols):
        trace.record(0, ('start', 0, c))
        if dfs(0, c, 0):
            return True
    return False

def word_search_bruteforce(board, word, trace):
    """Brute force: tries ALL possible paths of length len(word), including revisiting cells."""
    rows, cols = len(board), len(board[0])
    word_len = len(word)
    found_any = False
    
    def brute_path(path, i):
        nonlocal found_any
        if i == word_len:
            # Check if path spells the word (no marking, allows revisits)
            spelled = ''.join(board[r][c] for r, c in path)
            trace.record(i, ('validate', path))
            if spelled == word:
                found_any = True
                trace.record_solution()
            return
        
        for r in range(rows):
            for c in range(cols):
                # Try every cell as next step (no adjacency constraint = pure brute force)
                trace.record(i, ('try', r, c))
                brute_path(path + [(r, c)], i + 1)
    
    brute_path([], 0)
    return found_any


# ═══════════════════════════════════════════════════════════
# PROBLEM 3: SUDOKU
# ═══════════════════════════════════════════════════════════

SUDOKU_BOARD = [
    ["5", "3", ".", ".", "7", ".", ".", ".", "."],
    ["6", ".", ".", "1", "9", "5", ".", ".", "."],
    [".", "9", "8", ".", ".", ".", ".", "6", "."],
    ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
    ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
    ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
    [".", "6", ".", ".", ".", ".", "2", "8", "."],
    [".", ".", ".", "4", "1", "9", ".", ".", "5"],
    [".", ".", ".", ".", "8", ".", ".", "7", "9"]
]

def sudoku_possibilities(board, row, col):
    """Compute possible digits for cell (row, col)."""
    filled = set()
    for c in range(9):
        if board[row][c] != '.':
            filled.add(board[row][c])
    for r in range(9):
        if board[r][col] != '.':
            filled.add(board[r][col])
    br, bc = 3 * (row // 3), 3 * (col // 3)
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] != '.':
                filled.add(board[r][c])
    return [d for d in "123456789" if d not in filled]

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == '.':
                return (i, j)
    return None

def sudoku_correct(board, trace):
    """Correct backtracking with MRV heuristic."""
    board = copy.deepcopy(board)
    
    def solve():
        empty = find_empty(board)
        if empty is None:
            trace.record(0, ('solved',))
            trace.record_solution()
            return True
        
        r, c = empty
        possibilities = sudoku_possibilities(board, r, c)
        trace.record(0, ('cell', r, c, possibilities))
        
        for digit in possibilities:
            board[r][c] = digit
            trace.record(0, ('try', r, c, digit))
            if solve():
                return True
            board[r][c] = '.'
            trace.record(0, ('backtrack', r, c))
        
        return False
    
    solve()
    return board

def sudoku_partial(board, trace):
    """Partial: only tries digits 1-5 (incomplete search space)."""
    board = copy.deepcopy(board)
    
    def solve():
        empty = find_empty(board)
        if empty is None:
            trace.record(0, ('solved',))
            trace.record_solution()
            return True
        
        r, c = empty
        possibilities = sudoku_possibilities(board, r, c)
        # Partial: only try first 5 possibilities (simulating incomplete exploration)
        possibilities = possibilities[:5]
        trace.record(0, ('cell', r, c, possibilities))
        
        for digit in possibilities:
            board[r][c] = digit
            trace.record(0, ('try', r, c, digit))
            if solve():
                return True
            board[r][c] = '.'
            trace.record(0, ('backtrack', r, c))
        
        return False
    
    solve()
    return board

def sudoku_bruteforce(board, trace):
    """Brute force: tries all 9^empty_cells combinations."""
    board = copy.deepcopy(board)
    empty_cells = [(i, j) for i in range(9) for j in range(9) if board[i][j] == '.']
    n_empty = len(empty_cells)
    
    def try_all(idx):
        if idx == n_empty:
            # Validate entire board
            trace.record(0, ('validate_all',))
            valid = True
            for i in range(9):
                for j in range(9):
                    for di in range(9):
                        if di != i and board[di][j] == board[i][j]:
                            valid = False
                    for dj in range(9):
                        if dj != j and board[i][dj] == board[i][j]:
                            valid = False
                    br, bc = 3 * (i // 3), 3 * (j // 3)
                    for r in range(br, br + 3):
                        for c in range(bc, bc + 3):
                            if (r, c) != (i, j) and board[r][c] == board[i][j]:
                                valid = False
            if valid:
                trace.record_solution()
            return
        
        r, c = empty_cells[idx]
        for digit in "123456789":
            board[r][c] = digit
            trace.record(0, ('assign', r, c, digit, f'cell_{idx}'))
            try_all(idx + 1)
        board[r][c] = '.'
    
    try_all(0)
    return board


# ═══════════════════════════════════════════════════════════
# EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════

def run_experiment():
    problems = []
    
    # ── Problem 1: N-Queens ──
    print("=" * 80)
    print("PROBLEM 1: N-QUEENS (n=6)")
    print("=" * 80)
    
    nq_results = {}
    for label, solver_fn in [
        ('correct', lambda t: nqueens_correct(6, t)),
        ('partial', lambda t: nqueens_partial(6, t)),
        ('bruteforce', lambda t: nqueens_bruteforce(6, t)),
    ]:
        trace = GrowthTrace()
        sols = solver_fn(trace)
        curve = trace.compute_growth_curve()
        curvature = trace.compute_curvature()
        
        nq_results[label] = {
            'solutions': trace.solutions_found,
            'total_steps': trace.step_count,
            'unique_states': curve[-1]['cumulative_unique'] if curve else 0,
            'curvature': curvature,
        }
        
        print(f"\n  {label}:")
        print(f"    solutions: {trace.solutions_found}")
        print(f"    total_steps: {trace.step_count}")
        print(f"    unique_states: {curve[-1]['cumulative_unique'] if curve else 0}")
        print(f"    curvature: {curvature['curvature']}")
        print(f"    r_squared: {curvature['r_squared']}")
    
    problems.append(('N-Queens (n=6)', nq_results))
    
    # ── Problem 2: Word Search ──
    print("\n" + "=" * 80)
    print("PROBLEM 2: WORD SEARCH")
    print("=" * 80)
    
    ws_results = {}
    for label, solver_fn in [
        ('correct', lambda t: word_search_correct(copy.deepcopy(WS_BOARD), WS_WORD, t)),
        ('partial', lambda t: word_search_partial(copy.deepcopy(WS_BOARD), WS_WORD, t)),
        ('bruteforce', lambda t: word_search_bruteforce(copy.deepcopy(WS_BOARD), WS_WORD, t)),
    ]:
        trace = GrowthTrace()
        try:
            result = solver_fn(trace)
        except RecursionError:
            print(f"\n  {label}: RecursionError (brute force too deep)")
            ws_results[label] = {
                'solutions': 'RecursionError',
                'total_steps': trace.step_count,
                'unique_states': 0,
                'curvature': {'curvature': 'N/A', 'r_squared': 0},
            }
            continue
        
        curve = trace.compute_growth_curve()
        curvature = trace.compute_curvature()
        
        ws_results[label] = {
            'found': result,
            'total_steps': trace.step_count,
            'unique_states': curve[-1]['cumulative_unique'] if curve else 0,
            'curvature': curvature,
        }
        
        print(f"\n  {label}:")
        print(f"    found: {result}")
        print(f"    total_steps: {trace.step_count}")
        print(f"    unique_states: {curve[-1]['cumulative_unique'] if curve else 0}")
        print(f"    curvature: {curvature['curvature']}")
        print(f"    r_squared: {curvature['r_squared']}")
    
    problems.append(('Word Search', ws_results))
    
    # ── Problem 3: Sudoku ──
    print("\n" + "=" * 80)
    print("PROBLEM 3: SUDOKU")
    print("=" * 80)
    
    sd_results = {}
    for label, solver_fn in [
        ('correct', lambda t: sudoku_correct(copy.deepcopy(SUDOKU_BOARD), t)),
        ('partial', lambda t: sudoku_partial(copy.deepcopy(SUDOKU_BOARD), t)),
        ('bruteforce', lambda t: sudoku_bruteforce(copy.deepcopy(SUDOKU_BOARD), t)),
    ]:
        trace = GrowthTrace()
        try:
            result = solver_fn(trace)
        except RecursionError:
            print(f"\n  {label}: RecursionError (brute force too deep)")
            sd_results[label] = {
                'solutions': 'RecursionError',
                'total_steps': trace.step_count,
                'unique_states': 0,
                'curvature': {'curvature': 'N/A', 'r_squared': 0},
            }
            continue
        
        curve = trace.compute_growth_curve()
        curvature = trace.compute_curvature()
        
        sd_results[label] = {
            'total_steps': trace.step_count,
            'unique_states': curve[-1]['cumulative_unique'] if curve else 0,
            'curvature': curvature,
        }
        
        print(f"\n  {label}:")
        print(f"    total_steps: {trace.step_count}")
        print(f"    unique_states: {curve[-1]['cumulative_unique'] if curve else 0}")
        print(f"    curvature: {curvature['curvature']}")
        print(f"    r_squared: {curvature['r_squared']}")
    
    problems.append(('Sudoku', sd_results))
    
    # ═══════════════════════════════════════════════════════════
    # SEPARATION ANALYSIS
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "=" * 80)
    print("CROSS-PROBLEM CURVATURE SEPARATION")
    print("=" * 80)
    
    for prob_name, results in problems:
        print(f"\n--- {prob_name} ---")
        print(f"  {'Regime':<15s} | {'Steps':>10s} | {'Unique':>8s} | {'Curvature':>12s} | {'R²':>6s}")
        print(f"  {'-'*15}-+-{'-'*10}-+-{'-'*8}-+-{'-'*12}-+-{'-'*6}")
        
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime not in results:
                continue
            r = results[regime]
            curv = r['curvature']
            curv_val = curv['curvature'] if isinstance(curv, dict) else curv
            r2 = curv['r_squared'] if isinstance(curv, dict) else 0
            steps = r['total_steps']
            unique = r['unique_states']
            
            curv_str = f"{curv_val:.6f}" if isinstance(curv_val, (int, float)) else str(curv_val)
            r2_str = f"{r2:.4f}" if isinstance(r2, (int, float)) else str(r2)
            
            print(f"  {regime:<15s} | {steps:>10d} | {unique:>8d} | {curv_str:>12s} | {r2_str:>6s}")
    
    # ═══════════════════════════════════════════════════════════
    # CURVATURE BOUNDARY TEST
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "=" * 80)
    print("CURVATURE BOUNDARY TEST")
    print("=" * 80)
    
    print("\n  Does curvature consistently separate regimes across problems?")
    print("  Expected: bruteforce >> correct > partial")
    
    for prob_name, results in problems:
        curvs = {}
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime in results:
                c = results[regime]['curvature']
                if isinstance(c, dict):
                    curvs[regime] = c['curvature']
        
        if len(curvs) < 3:
            print(f"\n  {prob_name}: INCOMPLETE (missing regimes)")
            continue
        
        bf = curvs['bruteforce']
        co = curvs['correct']
        pa = curvs['partial']
        
        # Check ordering
        if isinstance(bf, (int, float)) and isinstance(co, (int, float)) and isinstance(pa, (int, float)):
            passes = (bf > co > pa)
            print(f"\n  {prob_name}: curvature: bf={bf:.4f}, correct={co:.4f}, partial={pa:.4f} → {'PASS' if passes else 'FAIL'}")
        else:
            print(f"\n  {prob_name}: non-numeric curvature values")
    
    # ═══════════════════════════════════════════════════════════
    # SAVE RESULTS
    # ═══════════════════════════════════════════════════════════
    
    # Convert to JSON-serializable format
    serializable = {}
    for prob_name, results in problems:
        serializable[prob_name] = {}
        for regime, r in results.items():
            serializable[prob_name][regime] = {
                'solutions': r.get('solutions', r.get('found', 'N/A')),
                'total_steps': r['total_steps'],
                'unique_states': r['unique_states'],
                'curvature': r['curvature'],
            }
    
    output_path = r'F:\pythonProject\scratch\curvature_cross_problem.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, indent=2, default=str)
    
    print(f"\n  Results saved to: {output_path}")


if __name__ == '__main__':
    run_experiment()
