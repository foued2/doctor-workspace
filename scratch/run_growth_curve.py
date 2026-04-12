"""
S-DIMENSION: STATE-SPACE GROWTH CURVE EXPERIMENT

Measures S(t) = cumulative state-space expansion over recursive depth.
Tests separability across n=4, n=6, n=8 for:
  - backtracking (correct, finds all solutions)
  - partial backtracking (finds first solution, stops)
  - brute-force (n^n enumeration)

Output: growth curves + shape separation analysis.
"""

import copy
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

# ─── Solvers with depth-traced state tracking ───────────────────────────

def is_valid(board, row, col):
    """Standard N-Queens validity check."""
    for r in range(row):
        c = board[r]
        if c == col or abs(c - col) == abs(r - row):
            return False
    return True


class GrowthTrace:
    """
    Tracks state-space growth as a function of decision depth.
    
    S(t) = cumulative states explored up to depth t
    branching[t] = number of branches attempted at depth t
    """
    def __init__(self):
        self.depth_states = {}   # depth -> list of states seen at that depth
        self.depth_calls = {}    # depth -> number of calls at that depth
        self.cumulative_states = []  # S(t): cumulative count at each step
        self.total_calls = 0
        self.max_depth = 0
        self.solutions_found = 0
        self.solution_depths = []
        
    def record_call(self, depth, board):
        self.total_calls += 1
        self.max_depth = max(self.max_depth, depth)
        
        if depth not in self.depth_states:
            self.depth_states[depth] = []
            self.depth_calls[depth] = 0
        
        self.depth_calls[depth] += 1
        state_key = tuple(board[:depth+1])  # partial board state up to current depth
        self.depth_states[depth].append(state_key)
    
    def record_solution(self, depth):
        self.solutions_found += 1
        self.solution_depths.append(depth)
    
    def compute_growth_curve(self):
        """
        Compute S(t) = cumulative state count up to depth t.
        Returns list of (depth, cumulative_states, cumulative_calls).
        """
        curve = []
        cum_states = 0
        cum_calls = 0
        
        for depth in range(self.max_depth + 1):
            states_at_depth = len(self.depth_states.get(depth, []))
            calls_at_depth = self.depth_calls.get(depth, 0)
            cum_states += states_at_depth
            cum_calls += calls_at_depth
            curve.append({
                'depth': depth,
                'states_at_depth': states_at_depth,
                'calls_at_depth': calls_at_depth,
                'cumulative_states': cum_states,
                'cumulative_calls': cum_calls,
            })
        
        return curve


def solve_nqueens_backtracking(n):
    """Correct backtracking: finds ALL solutions."""
    trace = GrowthTrace()
    solutions = []
    
    def backtrack(row, board):
        trace.record_call(row, board)
        
        if row == n:
            solutions.append(copy.deepcopy(board))
            trace.record_solution(row)
            return
        
        for col in range(n):
            if is_valid(board, row, col):
                board[row] = col
                backtrack(row + 1, board)
                board[row] = -1
    
    backtrack(0, [-1] * n)
    return solutions, trace


def solve_nqueens_partial(n):
    """Partial backtracking: finds FIRST solution then stops."""
    trace = GrowthTrace()
    solutions = []
    
    def backtrack(row, board):
        trace.record_call(row, board)
        
        if row == n:
            solutions.append(copy.deepcopy(board))
            trace.record_solution(row)
            return True
        
        for col in range(n):
            if is_valid(board, row, col):
                board[row] = col
                if backtrack(row + 1, board):
                    return True
                board[row] = -1
    
    backtrack(0, [-1] * n)
    return solutions, trace


def solve_nqueens_bruteforce(n):
    """Brute force: enumerates all n^n candidates."""
    trace = GrowthTrace()
    solutions = []
    
    def generate(row, board):
        if row == n:
            trace.record_call(row, board)
            # Validate full board
            valid = True
            for i in range(n):
                for j in range(i):
                    if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                        valid = False
                        break
                if not valid:
                    break
            if valid:
                solutions.append(copy.deepcopy(board))
                trace.record_solution(row)
            return
        
        for col in range(n):
            board[row] = col
            trace.record_call(row, board)
            generate(row + 1, board)
            board[row] = -1
    
    generate(0, [-1] * n)
    return solutions, trace


# ─── Analysis ────────────────────────────────────────────────────────────

def compute_growth_signature(curve):
    """
    Reduce growth curve to a single signature:
    - growth_rate: how fast cumulative states grow per depth
    - curvature: acceleration/deceleration of growth
    - total_work: total calls
    - efficiency: solutions_found / total_calls
    """
    if not curve:
        return {'growth_rate': 0, 'curvature': 0, 'total_work': 0, 'efficiency': 0}
    
    total_calls = curve[-1]['cumulative_calls']
    total_states = curve[-1]['cumulative_states']
    max_depth = curve[-1]['depth']
    
    # Growth rate: average states per depth level
    growth_rate = total_states / (max_depth + 1) if max_depth >= 0 else 0
    
    # Curvature: compare first half growth to second half growth
    mid = len(curve) // 2
    if mid > 0 and len(curve) > mid:
        first_half_states = curve[mid]['cumulative_states']
        second_half_states = total_states - first_half_states
        curvature = (second_half_states - first_half_states) / total_states if total_states > 0 else 0
    else:
        curvature = 0
    
    return {
        'growth_rate': round(growth_rate, 2),
        'curvature': round(curvature, 4),
        'total_work': total_calls,
        'max_depth': max_depth,
    }


def print_ascii_curve(curve, label, width=60):
    """Print an ASCII visualization of cumulative states vs depth."""
    if not curve:
        print(f"  {label}: (empty)")
        return
    
    max_val = max(c['cumulative_states'] for c in curve) or 1
    max_depth = curve[-1]['depth']
    
    print(f"\n  {label}")
    print(f"  {'depth':>5s} | {'cum_states':>10s} | {'cum_calls':>10s} | bar")
    print(f"  {'-'*5}-+-{'-'*10}-+-{'-'*10}-+-{'-'*width}")
    
    for c in curve:
        depth = c['depth']
        cs = c['cumulative_states']
        cc = c['cumulative_calls']
        bar_len = int((cs / max_val) * width)
        bar = '█' * bar_len
        print(f"  {depth:5d} | {cs:10d} | {cc:10d} | {bar}")


# ─── Main experiment ─────────────────────────────────────────────────────

def run_experiment():
    N_VALUES = [4, 6, 8]
    SOLVERS = [
        ('backtracking_correct', solve_nqueens_backtracking, 'Correct backtracking (all solutions)'),
        ('partial', solve_nqueens_partial, 'Partial backtracking (first solution)'),
        ('bruteforce', solve_nqueens_bruteforce, 'Brute force (n^n enumeration)'),
    ]
    
    all_results = {}
    
    for n in N_VALUES:
        print(f"\n{'='*80}")
        print(f"  N-QUEENS n={n}")
        print(f"{'='*80}")
        
        n_results = {}
        
        for solver_key, solver_fn, solver_desc in SOLVERS:
            print(f"\n--- {solver_desc} ---")
            solutions, trace = solver_fn(n)
            curve = trace.compute_growth_curve()
            signature = compute_growth_signature(curve)
            
            n_results[solver_key] = {
                'description': solver_desc,
                'solutions_found': trace.solutions_found,
                'total_calls': trace.total_calls,
                'max_depth': trace.max_depth,
                'curve': curve,
                'signature': signature,
            }
            
            # Print summary
            print(f"  Solutions found: {trace.solutions_found}")
            print(f"  Total calls: {trace.total_calls}")
            print(f"  Max depth: {trace.max_depth}")
            print(f"  Growth rate: {signature['growth_rate']}")
            print(f"  Curvature: {signature['curvature']}")
            
            # ASCII curve (compact for larger n)
            if n <= 6:
                print_ascii_curve(curve, solver_key)
            else:
                # For n=8, print summary only
                print(f"  Curve: {len(curve)} depth levels, {curve[-1]['cumulative_states']} cumulative states")
        
        all_results[f'n{n}'] = n_results
    
    # ─── Separation analysis ─────────────────────────────────────────────
    
    print(f"\n{'='*80}")
    print(f"  SEPARATION ANALYSIS")
    print(f"{'='*80}")
    
    for n in N_VALUES:
        print(f"\n--- n={n} ---")
        n_results = all_results[f'n{n}']
        
        print(f"  {'Solver':<30s} | {'Solutions':>9s} | {'Calls':>10s} | {'Growth Rate':>11s} | {'Curvature':>9s}")
        print(f"  {'-'*30}-+-{'-'*9}-+-{'-'*10}-+-{'-'*11}-+-{'-'*9}")
        
        for solver_key in ['backtracking_correct', 'partial', 'bruteforce']:
            r = n_results[solver_key]
            sig = r['signature']
            print(f"  {solver_key:<30s} | {r['solutions_found']:9d} | {r['total_calls']:10d} | {sig['growth_rate']:11.2f} | {sig['curvature']:9.4f}")
        
        # Check separation: do signatures form distinct clusters?
        bc_sig = n_results['backtracking_correct']['signature']
        p_sig = n_results['partial']['signature']
        bf_sig = n_results['bruteforce']['signature']
        
        # Separation metric: ratio of total_work between regimes
        if bc_sig['total_work'] > 0:
            bf_bc_ratio = bf_sig['total_work'] / bc_sig['total_work']
        else:
            bf_bc_ratio = float('inf')
        
        if p_sig['total_work'] > 0:
            p_bc_ratio = p_sig['total_work'] / bc_sig['total_work']
        else:
            p_bc_ratio = 0
        
        print(f"\n  Separation ratios:")
        print(f"    bruteforce / backtracking = {bf_bc_ratio:.1f}x")
        print(f"    partial / backtracking = {p_bc_ratio:.2f}x")
        
        # Growth rate separation
        if bc_sig['growth_rate'] > 0:
            gr_bf_bc = bf_sig['growth_rate'] / bc_sig['growth_rate']
            gr_p_bc = p_sig['growth_rate'] / bc_sig['growth_rate']
        else:
            gr_bf_bc = float('inf')
            gr_p_bc = 0
        
        print(f"    growth_rate bruteforce/backtracking = {gr_bf_bc:.2f}x")
        print(f"    growth_rate partial/backtracking = {gr_p_bc:.2f}x")
    
    # ─── Cross-n stability ───────────────────────────────────────────────
    
    print(f"\n{'='*80}")
    print(f"  CROSS-n STABILITY")
    print(f"{'='*80}")
    
    print(f"\n  {'Ratio':<30s} | {'n=4':>8s} | {'n=6':>8s} | {'n=8':>8s}")
    print(f"  {'-'*30}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}")
    
    for ratio_name in ['bf_bc_work', 'p_bc_work', 'bf_bc_gr', 'p_bc_gr']:
        values = []
        for n in N_VALUES:
            n_results = all_results[f'n{n}']
            bc = n_results['backtracking_correct']['signature']
            p = n_results['partial']['signature']
            bf = n_results['bruteforce']['signature']
            
            if ratio_name == 'bf_bc_work':
                val = bf['total_work'] / bc['total_work'] if bc['total_work'] > 0 else float('inf')
            elif ratio_name == 'p_bc_work':
                val = p['total_work'] / bc['total_work'] if bc['total_work'] > 0 else 0
            elif ratio_name == 'bf_bc_gr':
                val = bf['growth_rate'] / bc['growth_rate'] if bc['growth_rate'] > 0 else float('inf')
            elif ratio_name == 'p_bc_gr':
                val = p['growth_rate'] / bc['growth_rate'] if bc['growth_rate'] > 0 else 0
            values.append(val)
        
        print(f"  {ratio_name:<30s} | {values[0]:8.2f} | {values[1]:8.2f} | {values[2]:8.2f}")
    
    # ─── Save results ────────────────────────────────────────────────────
    
    # Convert curve data to serializable format
    serializable_results = {}
    for n_key, n_results in all_results.items():
        serializable_results[n_key] = {}
        for solver_key, r in n_results.items():
            serializable_results[n_key][solver_key] = {
                'description': r['description'],
                'solutions_found': r['solutions_found'],
                'total_calls': r['total_calls'],
                'max_depth': r['max_depth'],
                'signature': r['signature'],
                'curve_summary': [
                    {'depth': c['depth'], 'cumulative_states': c['cumulative_states'], 
                     'cumulative_calls': c['cumulative_calls'], 'states_at_depth': c['states_at_depth']}
                    for c in r['curve']
                ]
            }
    
    output_path = r'F:\pythonProject\scratch\growth_curve_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n  Results saved to: {output_path}")
    print(f"  Full curve data in JSON for further analysis.")


if __name__ == '__main__':
    run_experiment()
