from collections import defaultdict
import copy
import sys
sys.stdout.reconfigure(encoding='utf-8')

def is_valid(board, row, col):
    for r in range(row):
        c = board[r]
        if c == col or abs(c - col) == abs(r - row):
            return False
    return True

class Trace:
    def __init__(self):
        self.calls = 0
        self.states = 0
        self.state_seen = defaultdict(int)
        self.paths = set()
    def record_state(self, board):
        key = tuple(board)
        self.state_seen[key] += 1
        self.states += 1
    def record_call(self):
        self.calls += 1
    def record_path(self, path_signature):
        self.paths.add(path_signature)

def solve_nqueens_backtracking(n):
    trace = Trace()
    solutions = []
    def backtrack(row, board, path):
        trace.record_call()
        trace.record_state(board)
        if row == n:
            solutions.append(copy.deepcopy(board))
            trace.record_path(tuple(path))
            return
        for col in range(n):
            if is_valid(board, row, col):
                board[row] = col
                backtrack(row + 1, board, path + [col])
                board[row] = -1
    backtrack(0, [-1] * n, [])
    return solutions, trace

def solve_nqueens_bruteforce(n):
    trace = Trace()
    solutions = []
    import itertools
    for perm in itertools.product(range(n), repeat=n):
        trace.record_call()
        trace.record_state(list(perm))
        valid = True
        for i in range(n):
            for j in range(i):
                if perm[i] == perm[j] or abs(perm[i] - perm[j]) == abs(i - j):
                    valid = False
        if valid:
            solutions.append(list(perm))
            trace.record_path(tuple(perm))
    return solutions, trace

def solve_nqueens_partial(n):
    """Backtracking that stops after finding first solution."""
    trace = Trace()
    solutions = []
    def backtrack(row, board, path):
        trace.record_call()
        trace.record_state(board)
        if row == n:
            solutions.append(copy.deepcopy(board))
            trace.record_path(tuple(path))
            return True
        for col in range(n):
            if is_valid(board, row, col):
                board[row] = col
                if backtrack(row + 1, board, path + [col]):
                    return True
                board[row] = -1
    backtrack(0, [-1] * n, [])
    return solutions, trace

def extract_features(solutions, trace, expected_count):
    F1 = trace.calls
    F2 = trace.states
    F3 = sum(v - 1 for v in trace.state_seen.values())
    F5 = len(trace.paths)
    return {
        'F1_control_flow': F1,
        'F2_state_expansion': F2,
        'F3_redundancy': F3,
        'F5_path_diversity': F5,
        'solution_count': len(solutions),
        'expected_count': expected_count
    }

n = 4
expected = 2

print("=" * 70)
print("N-QUEENS (n=4) — TRACE FEATURE EXPERIMENT")
print("=" * 70)

for label, solver in [
    ("BACKTRACKING (correct)", solve_nqueens_backtracking),
    ("BACKTRACKING (partial)", solve_nqueens_partial),
    ("BRUTE FORCE (permutations)", solve_nqueens_bruteforce),
]:
    print(f"\n--- {label} ---")
    sols, trace = solver(n)
    features = extract_features(sols, trace, expected)
    for k, v in features.items():
        print(f"  {k:<25s}: {v}")

print(f"\n{'=' * 70}")
print("FEATURE RATIOS (BRUTE / BACKTRACK)")
print("=" * 70)

_, t_bt = solve_nqueens_backtracking(n)
f_bt = extract_features([], t_bt, expected)
_, t_bf = solve_nqueens_bruteforce(n)
f_bf = extract_features([], t_bf, expected)

for k in ['F1_control_flow', 'F2_state_expansion', 'F3_redundancy', 'F5_path_diversity']:
    ratio = f_bf[k] / f_bt[k] if f_bt[k] > 0 else float('inf')
    print(f"  {k:<25s}: {ratio:.1f}x")
