"""
S-DIMENSION CROSS-PROBLEM VALIDATION — V2
===========================================
Key insight from V1 failure: quadratic curvature of cumulative states is WRONG.
Cumulative counts are monotonically non-decreasing → always positive curvature
or flat. The signal is in the GROWTH RATE (derivative), not the curve shape.

NEW APPROACH: 
  S(t) = cumulative states at step t
  growth_rate(t) = S(t) - S(t-1)  (states added per step)
  
  Classification:
  - brute force: growth rate accelerates or stays high (exponential)
  - correct backtracking: growth rate peaks then declines (pruned search)
  - partial: growth rate truncated early (incomplete exploration)

  Single metric: growth_rate_decay = (peak_rate - final_rate) / peak_rate
    - backtracking: high decay (prunes, rate drops)
    - brute force: low/negative decay (keeps growing)
    - partial: mid decay (stops early but had some pruning)
"""

import copy
import sys
import json
import math
sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
# GROWTH TRACE V2 — tracks growth rate dynamics
# ═══════════════════════════════════════════════════════════

class GrowthTraceV2:
    """
    Tracks execution growth rate over decision steps.
    """
    def __init__(self):
        self.step_count = 0
        self.solutions_found = 0
        self.cumulative_states = []  # S(t) at each step
        self.unique_seen = set()
    
    def record(self, state_key):
        self.step_count += 1
        key = str(state_key)
        if key not in self.unique_seen:
            self.unique_seen.add(key)
        self.cumulative_states.append(len(self.unique_seen))
    
    def record_solution(self):
        self.solutions_found += 1
    
    def compute_growth_rates(self):
        """
        Compute growth rate at each step: dS/dt = S(t) - S(t-1)
        Returns list of growth rates.
        """
        if not self.cumulative_states:
            return []
        
        rates = [self.cumulative_states[0]]  # first step
        for i in range(1, len(self.cumulative_states)):
            rate = self.cumulative_states[i] - self.cumulative_states[i-1]
            rates.append(rate)
        return rates
    
    def compute_classification(self):
        """
        Classify the execution based on growth rate dynamics.
        
        Returns dict with:
          - peak_rate: maximum growth rate observed
          - final_rate: average growth rate in last 20% of execution
          - decay_ratio: (peak - final) / peak (how much does search slow down?)
          - total_steps: number of decision steps
          - total_unique: total unique states explored
          - regime: predicted regime (bruteforce / backtracking / partial)
        """
        rates = self.compute_growth_rates()
        if not rates:
            return {'error': 'no data', 'regime': 'unknown'}
        
        peak_rate = max(rates)
        
        # Final rate: average of last 20%
        tail_start = int(len(rates) * 0.8)
        tail_rates = rates[tail_start:] if tail_start < len(rates) else rates[-1:]
        final_rate = sum(tail_rates) / len(tail_rates)
        
        # Decay ratio
        decay_ratio = (peak_rate - final_rate) / peak_rate if peak_rate > 0 else 0
        
        # Growth acceleration: compare first half avg rate to second half avg rate
        mid = len(rates) // 2
        first_half_avg = sum(rates[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(rates[mid:]) / (len(rates) - mid) if len(rates) > mid else 0
        acceleration = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0
        
        total_unique = self.cumulative_states[-1] if self.cumulative_states else 0
        
        # Classification rule (reference-free):
        # - acceleration > 0.5 → brute force (keeps growing)
        # - acceleration < -0.3 AND decay_ratio > 0.5 → backtracking (prunes hard)
        # - otherwise → partial (incomplete exploration)
        if acceleration > 0.5:
            regime = 'bruteforce'
        elif decay_ratio > 0.5 and acceleration < 0:
            regime = 'backtracking'
        else:
            regime = 'partial'
        
        return {
            'peak_rate': peak_rate,
            'final_rate': round(final_rate, 4),
            'decay_ratio': round(decay_ratio, 4),
            'acceleration': round(acceleration, 4),
            'total_steps': self.step_count,
            'total_unique': total_unique,
            'regime': regime,
        }


# ═══════════════════════════════════════════════════════════
# PROBLEM 1: N-QUEENS (n=6)
# ═══════════════════════════════════════════════════════════

def is_valid_nq(board, row, col):
    for r in range(row):
        c = board[r]
        if c == col or abs(c - col) == abs(r - row):
            return False
    return True

def nq_correct(n, trace):
    solutions = []
    def backtrack(row, board):
        trace.record(('call', row, tuple(board)))
        if row == n:
            solutions.append(copy.deepcopy(board))
            trace.record_solution()
            return
        for col in range(n):
            if is_valid_nq(board, row, col):
                board[row] = col
                trace.record(('place', row, col))
                backtrack(row + 1, board)
                board[row] = -1
    backtrack(0, [-1] * n)
    return solutions

def nq_partial(n, trace):
    solutions = []
    def backtrack(row, board):
        trace.record(('call', row, tuple(board)))
        if row == n:
            solutions.append(copy.deepcopy(board))
            trace.record_solution()
            return True
        for col in range(n):
            if is_valid_nq(board, row, col):
                board[row] = col
                trace.record(('place', row, col))
                if backtrack(row + 1, board):
                    return True
                board[row] = -1
    backtrack(0, [-1] * n)
    return solutions

def nq_bruteforce(n, trace):
    solutions = []
    def generate(row, board):
        if row == n:
            trace.record(('validate', tuple(board)))
            valid = True
            for i in range(n):
                for j in range(i):
                    if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                        valid = False
                        break
            if valid:
                solutions.append(copy.deepcopy(board))
                trace.record_solution()
            return
        for col in range(n):
            board[row] = col
            trace.record(('assign', row, col))
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
WS_WORD = "ABCCED"

def ws_correct(board, word, trace):
    rows, cols = len(board), len(board[0])
    def dfs(r, c, i):
        trace.record(('dfs', r, c, i))
        if i == len(word):
            trace.record_solution()
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[i]:
            return False
        tmp = board[r][c]
        board[r][c] = '#'
        trace.record(('mark', r, c))
        found = (dfs(r+1, c, i+1) or dfs(r-1, c, i+1) or
                 dfs(r, c+1, i+1) or dfs(r, c-1, i+1))
        board[r][c] = tmp
        trace.record(('unmark', r, c))
        return found
    for r in range(rows):
        for c in range(cols):
            trace.record(('start', r, c))
            if dfs(r, c, 0):
                return True
    return False

def ws_partial(board, word, trace):
    """Partial: only explores 2 directions instead of 4, starts from fewer cells."""
    rows, cols = len(board), len(board[0])
    def dfs(r, c, i):
        trace.record(('dfs', r, c, i))
        if i == len(word):
            trace.record_solution()
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[i]:
            return False
        tmp = board[r][c]
        board[r][c] = '#'
        trace.record(('mark', r, c))
        # Only 2 directions (incomplete exploration)
        found = dfs(r+1, c, i+1) or dfs(r, c+1, i+1)
        board[r][c] = tmp
        trace.record(('unmark', r, c))
        return found
    # Only start from first 2 cells of first row
    for c in range(min(2, cols)):
        trace.record(('start', 0, c))
        if dfs(0, c, 0):
            return True
    return False

def ws_bruteforce(board, word, trace):
    """Brute force: tries all cell sequences of length len(word), allowing revisits."""
    rows, cols = len(board), len(board[0])
    word_len = len(word)
    found_any = False
    
    def brute_path(path, i):
        nonlocal found_any
        if i == word_len:
            spelled = ''.join(board[r][c] for r, c in path)
            trace.record(('validate',))
            if spelled == word:
                found_any = True
                trace.record_solution()
            return
        for r in range(rows):
            for c in range(cols):
                trace.record(('try', r, c, i))
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

def sudoku_poss(board, row, col):
    filled = set()
    for c in range(9):
        if board[row][c] != '.': filled.add(board[row][c])
    for r in range(9):
        if board[r][col] != '.': filled.add(board[r][col])
    br, bc = 3 * (row // 3), 3 * (col // 3)
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] != '.': filled.add(board[r][c])
    return [d for d in "123456789" if d not in filled]

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == '.': return (i, j)
    return None

def sudoku_correct(board, trace):
    board = copy.deepcopy(board)
    def solve():
        empty = find_empty(board)
        if empty is None:
            trace.record(('solved',))
            trace.record_solution()
            return True
        r, c = empty
        poss = sudoku_poss(board, r, c)
        trace.record(('cell', r, c, len(poss)))
        for digit in poss:
            board[r][c] = digit
            trace.record(('try', r, c, digit))
            if solve(): return True
            board[r][c] = '.'
            trace.record(('backtrack', r, c))
        return False
    solve()
    return board

def sudoku_partial(board, trace):
    """Partial: limits search to first 3 possibilities per cell."""
    board = copy.deepcopy(board)
    def solve():
        empty = find_empty(board)
        if empty is None:
            trace.record(('solved',))
            trace.record_solution()
            return True
        r, c = empty
        poss = sudoku_poss(board, r, c)[:3]  # Partial: only 3 options
        trace.record(('cell', r, c, len(poss)))
        for digit in poss:
            board[r][c] = digit
            trace.record(('try', r, c, digit))
            if solve(): return True
            board[r][c] = '.'
            trace.record(('backtrack', r, c))
        return False
    solve()
    return board

def sudoku_bruteforce(board, trace):
    """Brute force: tries all 9^empty combinations. Limit to first 10 empty cells."""
    board = copy.deepcopy(board)
    empty_cells = [(i, j) for i in range(9) for j in range(9) if board[i][j] == '.']
    # LIMIT: only brute force first 15 empty cells (9^15 ≈ 2e14, still too much)
    # Use 8 cells instead: 9^8 ≈ 43M, manageable
    LIMIT = 8
    empty_cells = empty_cells[:LIMIT]
    n_empty = len(empty_cells)
    
    def try_all(idx):
        if idx == n_empty:
            trace.record(('validate_partial',))
            return
        r, c = empty_cells[idx]
        for digit in "123456789":
            board[r][c] = digit
            trace.record(('assign', r, c, digit, idx))
            try_all(idx + 1)
        board[r][c] = '.'
    
    try_all(0)
    return board


# ═══════════════════════════════════════════════════════════
# EXPERIMENT
# ═══════════════════════════════════════════════════════════

def run_experiment():
    problems = {}
    
    # ── N-Queens ──
    print("=" * 80)
    print("PROBLEM 1: N-QUEENS (n=6)")
    print("=" * 80)
    
    nq_results = {}
    for label, solver in [
        ('correct', lambda t: nq_correct(6, t)),
        ('partial', lambda t: nq_partial(6, t)),
        ('bruteforce', lambda t: nq_bruteforce(6, t)),
    ]:
        trace = GrowthTraceV2()
        solver(trace)
        classification = trace.compute_classification()
        nq_results[label] = classification
        print(f"  {label}: steps={classification['total_steps']}, "
              f"unique={classification['total_unique']}, "
              f"decay={classification['decay_ratio']}, "
              f"accel={classification['acceleration']}, "
              f"regime={classification['regime']}")
    
    problems['N-Queens (n=6)'] = nq_results
    
    # ── Word Search ──
    print("\n" + "=" * 80)
    print("PROBLEM 2: WORD SEARCH")
    print("=" * 80)
    
    ws_results = {}
    for label, solver in [
        ('correct', lambda t: ws_correct(copy.deepcopy(WS_BOARD), WS_WORD, t)),
        ('partial', lambda t: ws_partial(copy.deepcopy(WS_BOARD), WS_WORD, t)),
        ('bruteforce', lambda t: ws_bruteforce(copy.deepcopy(WS_BOARD), WS_WORD, t)),
    ]:
        trace = GrowthTraceV2()
        try:
            solver(trace)
        except RecursionError:
            ws_results[label] = {'error': 'RecursionError', 'regime': 'unknown'}
            print(f"  {label}: RecursionError")
            continue
        
        classification = trace.compute_classification()
        ws_results[label] = classification
        print(f"  {label}: steps={classification['total_steps']}, "
              f"unique={classification['total_unique']}, "
              f"decay={classification['decay_ratio']}, "
              f"accel={classification['acceleration']}, "
              f"regime={classification['regime']}")
    
    problems['Word Search'] = ws_results
    
    # ── Sudoku ──
    print("\n" + "=" * 80)
    print("PROBLEM 3: SUDOKU")
    print("=" * 80)
    
    sd_results = {}
    for label, solver in [
        ('correct', lambda t: sudoku_correct(copy.deepcopy(SUDOKU_BOARD), t)),
        ('partial', lambda t: sudoku_partial(copy.deepcopy(SUDOKU_BOARD), t)),
        ('bruteforce', lambda t: sudoku_bruteforce(copy.deepcopy(SUDOKU_BOARD), t)),
    ]:
        trace = GrowthTraceV2()
        try:
            solver(trace)
        except RecursionError:
            sd_results[label] = {'error': 'RecursionError', 'regime': 'unknown'}
            print(f"  {label}: RecursionError")
            continue
        
        classification = trace.compute_classification()
        sd_results[label] = classification
        print(f"  {label}: steps={classification['total_steps']}, "
              f"unique={classification['total_unique']}, "
              f"decay={classification['decay_ratio']}, "
              f"accel={classification['acceleration']}, "
              f"regime={classification['regime']}")
    
    problems['Sudoku'] = sd_results
    
    # ── Cross-Problem Analysis ──
    print("\n" + "=" * 80)
    print("CROSS-PROBLEM CLASSIFICATION SUMMARY")
    print("=" * 80)
    
    print(f"\n  {'Problem':<20s} | {'Regime':<15s} | {'decay':>8s} | {'accel':>8s} | {'Predicted':>12s}")
    print(f"  {'-'*20}-+-{'-'*15}-+-{'-'*8}-+-{'-'*8}-+-{'-'*12}")
    
    for prob_name, results in problems.items():
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime not in results:
                continue
            r = results[regime]
            decay = r.get('decay_ratio', 'N/A')
            accel = r.get('acceleration', 'N/A')
            predicted = r.get('regime', 'unknown')
            
            decay_str = f"{decay:.4f}" if isinstance(decay, (int, float)) else str(decay)
            accel_str = f"{accel:.4f}" if isinstance(accel, (int, float)) else str(accel)
            
            print(f"  {prob_name:<20s} | {regime:<15s} | {decay_str:>8s} | {accel_str:>8s} | {predicted:>12s}")
    
    # ── Acceptance Test ──
    print("\n" + "=" * 80)
    print("ACCEPTANCE TEST: Does classification match ground truth?")
    print("=" * 80)
    
    expected = {
        'correct': 'backtracking',
        'partial': 'partial',
        'bruteforce': 'bruteforce',
    }
    
    all_pass = True
    for prob_name, results in problems.items():
        print(f"\n  {prob_name}:")
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime not in results:
                print(f"    {regime}: MISSING")
                continue
            predicted = results[regime].get('regime', 'unknown')
            exp = expected[regime]
            match = predicted == exp
            status = "PASS" if match else "FAIL"
            if not match:
                all_pass = False
            print(f"    {regime} → predicted={predicted}, expected={exp} → {status}")
    
    print(f"\n  Overall: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
    
    # ── Save ──
    output_path = r'F:\pythonProject\scratch\curvature_v2_cross_problem.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(problems, f, indent=2, default=str)
    print(f"\n  Results saved to: {output_path}")


if __name__ == '__main__':
    run_experiment()
