"""
S-DIMENSION V3: TOTAL WORK vs UNIQUE STATES RATIO
==================================================
Hypothesis: the ratio of total decision steps to unique states explored
captures how much redundant work the algorithm does.

  S = total_steps / unique_states

Interpretation:
  - S ≈ 1.0: every step explores something new (efficient, linear)
  - S > 1.0: some redundancy (backtracking with revisits)
  - S >> 1.0: massive redundancy (brute force enumeration)

Also: partial solutions should have LOWER total work than correct ones
(since they stop early), even if the ratio is similar.

Test across 3 problems, 3 regimes each.
"""

import copy
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
# TRACE — minimal instrumentation
# ═══════════════════════════════════════════════════════════

class Trace:
    def __init__(self):
        self.steps = 0
        self.unique = set()
        self.solutions = 0
    
    def record(self, key):
        self.steps += 1
        self.unique.add(str(key))
    
    def record_solution(self):
        self.solutions += 1
    
    @property
    def ratio(self):
        u = len(self.unique)
        return self.steps / u if u > 0 else 0


# ═══════════════════════════════════════════════════════════
# N-QUEENS (n=6)
# ═══════════════════════════════════════════════════════════

def is_valid_nq(board, row, col):
    for r in range(row):
        if board[r] == col or abs(board[r] - col) == abs(r - row):
            return False
    return True

def nq_correct(n, t):
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

def nq_partial(n, t):
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

def nq_bruteforce(n, t):
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


# ═══════════════════════════════════════════════════════════
# WORD SEARCH
# ═══════════════════════════════════════════════════════════

WS = [['A','B','C','E'],['S','F','C','S'],['A','D','E','E']]
WW = "ABCCED"

def ws_correct(board, word, t):
    R, C = len(board), len(board[0])
    def dfs(r, c, i):
        t.record(('dfs', r, c, i))
        if i == len(word): t.record_solution(); return True
        if not (0<=r<R and 0<=c<C) or board[r][c] != word[i]: return False
        tmp = board[r][c]; board[r][c] = '#'; t.record(('mark', r, c))
        found = dfs(r+1,c,i+1) or dfs(r-1,c,i+1) or dfs(r,c+1,i+1) or dfs(r,c-1,i+1)
        board[r][c] = tmp; t.record(('unmark', r, c))
        return found
    return any(dfs(r,c,0) for r in range(R) for c in range(C))

def ws_partial(board, word, t):
    R, C = len(board), len(board[0])
    def dfs(r, c, i):
        t.record(('dfs', r, c, i))
        if i == len(word): t.record_solution(); return True
        if not (0<=r<R and 0<=c<C) or board[r][c] != word[i]: return False
        tmp = board[r][c]; board[r][c] = '#'; t.record(('mark', r, c))
        # Only 2 directions
        found = dfs(r+1,c,i+1) or dfs(r,c+1,i+1)
        board[r][c] = tmp; t.record(('unmark', r, c))
        return found
    # Only first 2 starting cells
    return any(dfs(0,c,0) for c in range(min(2, C)))

def ws_bruteforce(board, word, t):
    R, C = len(board), len(board[0])
    found = False
    def brute(path, i):
        nonlocal found
        if i == len(word):
            t.record(('validate',))
            if ''.join(board[r][c] for r,c in path) == word:
                found = True; t.record_solution()
            return
        for r in range(R):
            for c in range(C):
                t.record(('try', r, c, i))
                brute(path+[(r,c)], i+1)
    brute([], 0)
    return found


# ═══════════════════════════════════════════════════════════
# SUDOKU
# ═══════════════════════════════════════════════════════════

SUDOKU = [
    ["5","3",".",".","7",".",".",".","."],
    ["6",".",".","1","9","5",".",".","."],
    [".","9","8",".",".",".",".","6","."],
    ["8",".",".",".","6",".",".",".","3"],
    ["4",".",".","8",".","3",".",".","1"],
    ["7",".",".",".","2",".",".",".","6"],
    [".","6",".",".",".",".","2","8","."],
    [".",".",".","4","1","9",".",".","5"],
    [".",".",".",".","8",".",".","7","9"]
]

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

def sudoku_partial(board, t):
    """Partial: limits recursion depth — stops after 5 cells filled."""
    b = copy.deepcopy(board)
    def solve(depth=0):
        if depth >= 5:  # Partial: stop after 5 levels
            t.record(('depth_limit',))
            return False
        e = find_empty(b)
        if e is None: t.record(('solved',)); t.record_solution(); return True
        r, c = e; p = poss(b, r, c); t.record(('cell', r, c, len(p)))
        for d in p:
            b[r][c] = d; t.record(('try', r, c, d))
            if solve(depth+1): return True
            b[r][c] = '.'; t.record(('backtrack', r, c))
        return False
    solve(); return b

def sudoku_bruteforce(board, t):
    """Brute force: tries all 9^8 combos for first 8 empty cells."""
    b = copy.deepcopy(board)
    empties = [(i,j) for i in range(9) for j in range(9) if b[i][j]=='.'][:8]
    def go(idx):
        if idx == len(empties):
            t.record(('validate',))
            return
        r, c = empties[idx]
        for d in "123456789":
            b[r][c] = d; t.record(('assign', r, c, d, idx))
            go(idx+1)
        b[r][c] = '.'
    go(0); return b


# ═══════════════════════════════════════════════════════════
# EXPERIMENT
# ═══════════════════════════════════════════════════════════

def run():
    problems = {}
    
    for prob_name, runners in [
        ('N-Queens (n=6)', {
            'correct': lambda t: nq_correct(6, t),
            'partial': lambda t: nq_partial(6, t),
            'bruteforce': lambda t: nq_bruteforce(6, t),
        }),
        ('Word Search', {
            'correct': lambda t: ws_correct(copy.deepcopy(WS), WW, t),
            'partial': lambda t: ws_partial(copy.deepcopy(WS), WW, t),
            'bruteforce': lambda t: ws_bruteforce(copy.deepcopy(WS), WW, t),
        }),
        ('Sudoku', {
            'correct': lambda t: sudoku_correct(copy.deepcopy(SUDOKU), t),
            'partial': lambda t: sudoku_partial(copy.deepcopy(SUDOKU), t),
            'bruteforce': lambda t: sudoku_bruteforce(copy.deepcopy(SUDOKU), t),
        }),
    ]:
        print(f"\n{'='*80}")
        print(f"  {prob_name}")
        print(f"{'='*80}")
        
        results = {}
        for regime, fn in runners.items():
            t = Trace()
            try:
                fn(t)
            except RecursionError:
                results[regime] = {'error': 'RecursionError'}
                print(f"  {regime}: RecursionError")
                continue
            
            results[regime] = {
                'steps': t.steps,
                'unique': len(t.unique),
                'ratio': round(t.ratio, 4),
                'solutions': t.solutions,
            }
            print(f"  {regime}: steps={t.steps:,}, unique={len(t.unique):,}, "
                  f"ratio={t.ratio:.4f}, solutions={t.solutions}")
        
        problems[prob_name] = results
    
    # ── Analysis ──
    print(f"\n{'='*80}")
    print("  S = total_steps / unique_states (redundancy ratio)")
    print(f"{'='*80}")
    
    print(f"\n  {'Problem':<20s} | {'Regime':<12s} | {'Steps':>10s} | {'Unique':>8s} | {'S=ratio':>10s} | {'Solns':>5s}")
    print(f"  {'-'*20}-+-{'-'*12}-+-{'-'*10}-+-{'-'*8}-+-{'-'*10}-+-{'-'*5}")
    
    for pn, res in problems.items():
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime not in res: continue
            r = res[regime]
            if 'error' in r:
                print(f"  {pn:<20s} | {regime:<12s} | ERROR")
                continue
            print(f"  {pn:<20s} | {regime:<12s} | {r['steps']:>10,} | {r['unique']:>8,} | {r['ratio']:>10.4f} | {r['solutions']:>5d}")
    
    # ── Separation test ──
    print(f"\n{'='*80}")
    print("  SEPARATION: Can S distinguish regimes?")
    print(f"{'='*80}")
    print(f"\n  Hypothesis: bruteforce >> correct > partial  (in terms of S)")
    
    for pn, res in problems.items():
        vals = {}
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime in res and 'error' not in res[regime]:
                vals[regime] = res[regime]['ratio']
        
        if len(vals) < 3:
            print(f"\n  {pn}: incomplete data")
            continue
        
        # Check ordering
        bf_gt_co = vals['bruteforce'] > vals['correct']
        co_gt_pa = vals['correct'] > vals['partial']
        
        print(f"\n  {pn}:")
        print(f"    BF({vals['bruteforce']:.4f}) > Correct({vals['correct']:.4f})? {'YES' if bf_gt_co else 'NO'}")
        print(f"    Correct({vals['correct']:.4f}) > Partial({vals['partial']:.4f})? {'YES' if co_gt_pa else 'NO'}")
        print(f"    Separation: {'FULL' if (bf_gt_co and co_gt_pa) else 'PARTIAL' if (bf_gt_co or co_gt_pa) else 'NONE'}")
    
    # Also test total_work as alternative S
    print(f"\n{'='*80}")
    print("  ALTERNATIVE S: total_steps alone (absolute work)")
    print(f"{'='*80}")
    
    for pn, res in problems.items():
        vals = {}
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime in res and 'error' not in res[regime]:
                vals[regime] = res[regime]['steps']
        
        if len(vals) < 3:
            print(f"\n  {pn}: incomplete data")
            continue
        
        bf_gt_co = vals['bruteforce'] > vals['correct']
        co_gt_pa = vals['correct'] > vals['partial']
        
        print(f"\n  {pn}:")
        print(f"    BF({vals['bruteforce']:,}) > Correct({vals['correct']:,})? {'YES' if bf_gt_co else 'NO'}")
        print(f"    Correct({vals['correct']:,}) > Partial({vals['partial']:,})? {'YES' if co_gt_pa else 'NO'}")
        print(f"    Separation: {'FULL' if (bf_gt_co and co_gt_pa) else 'PARTIAL' if (bf_gt_co or co_gt_pa) else 'NONE'}")
        print(f"    BF/Correct ratio: {vals['bruteforce']/vals['correct']:.1f}x")
        print(f"    Correct/Partial ratio: {vals['correct']/vals['partial']:.1f}x")
    
    # Save
    output = {}
    for pn, res in problems.items():
        output[pn] = {}
        for regime, r in res.items():
            output[pn][regime] = {k: (str(v) if isinstance(v, set) else v) for k, v in r.items()}
    
    path = r'F:\pythonProject\scratch\s_v3_results.json'
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved: {path}")

if __name__ == '__main__':
    run()
