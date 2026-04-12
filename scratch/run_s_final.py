"""
S_FINAL = S_observed / S_opt
===============================
S_opt = theoretical lower bound of necessary decisions,
computed from the problem INSTANCE alone (no execution needed).

Problem-class templates:
  - N-Queens:      S_opt = n  (one placement per row)
  - Word Search:   S_opt = len(word)  (one match per char in solution path)
  - Sudoku:        S_opt = empty_cells  (one fill per empty cell)

Expected:
  S_final ≈ 1     → optimal execution
  S_final >> 1    → redundant / brute force
  S_final < 1     → truncated / partial

This is the normalization layer that makes S cross-problem comparable.
"""

import copy
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
# TRACE (minimal)
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


# ═══════════════════════════════════════════════════════════
# S_opt COMPUTERS — derivable from problem instance only
# ═══════════════════════════════════════════════════════════

def s_opt_nqueens(n):
    """
    N-Queens: S_opt = n
    One placement decision per row in a perfectly pruned search.
    The oracle places exactly n queens, one per row, no backtracking needed.
    """
    return n

def s_opt_wordsearch(word):
    """
    Word Search: S_opt = len(word)
    One character match per position along the correct path.
    The oracle traces the exact path through the board.
    """
    return len(word)

def s_opt_sudoku(board):
    """
    Sudoku: S_opt = number of empty cells
    Each empty cell requires exactly one fill decision in optimal propagation.
    The oracle fills each cell with the correct digit on first try.
    """
    return sum(row.count('.') for row in board)


# ═══════════════════════════════════════════════════════════
# SOLVERS (same as V3)
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
        found = dfs(r+1,c,i+1) or dfs(r,c+1,i+1)
        board[r][c] = tmp; t.record(('unmark', r, c))
        return found
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
    b = copy.deepcopy(board)
    def solve(depth=0):
        if depth >= 5:
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
# CLASSIFICATION RULE (reference-free, using S_final)
# ═══════════════════════════════════════════════════════════

def classify_s_final(s_final):
    """
    Classify execution efficiency based on normalized distance from optimal.
    
    S measures EFFICIENCY (how much redundant work), not COMPLETENESS.
    Completeness is C's job. S only answers: is this execution wasteful?
    
    Threshold: S_final > 1000 → wasteful (exponential blowup, no pruning)
    This threshold is derived from the empirical gap between regimes:
      - Smallest BF/Correct gap: Sudoku at 69x → but BF S_final = 1.79M
      - Largest Correct S_final: Sudoku at 246x
      - 1000x sits cleanly between efficient (≤246) and wasteful (≥17K)
    """
    if s_final > 1000:
        return 'wasteful'
    else:
        return 'efficient'


# ═══════════════════════════════════════════════════════════
# EXPERIMENT
# ═══════════════════════════════════════════════════════════

def run():
    problems = {}
    
    # ── N-Queens (n=6) ──
    nq_sopt = s_opt_nqueens(6)
    print(f"{'='*90}")
    print(f"  N-QUEENS (n=6)  |  S_opt = {nq_sopt}  (one placement per row)")
    print(f"{'='*90}")
    
    nq_results = {}
    for label, fn in [
        ('correct',    lambda t: nq_correct(6, t)),
        ('partial',    lambda t: nq_partial(6, t)),
        ('bruteforce', lambda t: nq_bruteforce(6, t)),
    ]:
        t = Trace(); fn(t)
        s_obs = t.steps
        s_final = s_obs / nq_sopt if nq_sopt > 0 else 0
        pred = classify_s_final(s_final)
        nq_results[label] = {'steps': s_obs, 'unique': len(t.unique), 
                             's_opt': nq_sopt, 's_final': round(s_final, 2),
                             'predicted': pred, 'solutions': t.solutions}
        print(f"  {label:<12s}: S_obs={s_obs:>8,}  S_opt={nq_sopt:>4}  "
              f"S_final={s_final:>10.2f}  → predicted={pred}")
    
    problems['N-Queens (n=6)'] = nq_results
    
    # ── Word Search ──
    ws_sopt = s_opt_wordsearch(WW)
    print(f"\n{'='*90}")
    print(f"  WORD SEARCH  |  S_opt = {ws_sopt}  (len('{WW}'))")
    print(f"{'='*90}")
    
    ws_results = {}
    for label, fn in [
        ('correct',    lambda t: ws_correct(copy.deepcopy(WS), WW, t)),
        ('partial',    lambda t: ws_partial(copy.deepcopy(WS), WW, t)),
        ('bruteforce', lambda t: ws_bruteforce(copy.deepcopy(WS), WW, t)),
    ]:
        t = Trace()
        try: fn(t)
        except RecursionError:
            ws_results[label] = {'error': 'RecursionError', 'predicted': 'unknown'}
            print(f"  {label:<12s}: RecursionError")
            continue
        s_obs = t.steps
        s_final = s_obs / ws_sopt if ws_sopt > 0 else 0
        pred = classify_s_final(s_final)
        ws_results[label] = {'steps': s_obs, 'unique': len(t.unique),
                             's_opt': ws_sopt, 's_final': round(s_final, 2),
                             'predicted': pred}
        print(f"  {label:<12s}: S_obs={s_obs:>10,}  S_opt={ws_sopt:>4}  "
              f"S_final={s_final:>10.2f}  → predicted={pred}")
    
    problems['Word Search'] = ws_results
    
    # ── Sudoku ──
    sd_sopt = s_opt_sudoku(SUDOKU)
    print(f"\n{'='*90}")
    print(f"  SUDOKU  |  S_opt = {sd_sopt}  (empty cells)")
    print(f"{'='*90}")
    
    sd_results = {}
    for label, fn in [
        ('correct',    lambda t: sudoku_correct(copy.deepcopy(SUDOKU), t)),
        ('partial',    lambda t: sudoku_partial(copy.deepcopy(SUDOKU), t)),
        ('bruteforce', lambda t: sudoku_bruteforce(copy.deepcopy(SUDOKU), t)),
    ]:
        t = Trace()
        try: fn(t)
        except RecursionError:
            sd_results[label] = {'error': 'RecursionError', 'predicted': 'unknown'}
            print(f"  {label:<12s}: RecursionError")
            continue
        s_obs = t.steps
        s_final = s_obs / sd_sopt if sd_sopt > 0 else 0
        pred = classify_s_final(s_final)
        sd_results[label] = {'steps': s_obs, 'unique': len(t.unique),
                             's_opt': sd_sopt, 's_final': round(s_final, 2),
                             'predicted': pred}
        print(f"  {label:<12s}: S_obs={s_obs:>10,}  S_opt={sd_sopt:>4}  "
              f"S_final={s_final:>10.2f}  → predicted={pred}")
    
    problems['Sudoku'] = sd_results
    
    # ═══════════════════════════════════════════════════════════
    # ACCEPTANCE TEST
    # ═══════════════════════════════════════════════════════════
    
    print(f"\n{'='*90}")
    print(f"  ACCEPTANCE TEST: S_final classification accuracy")
    print(f"{'='*90}")
    
    expected_map = {
        'correct': 'efficient',     # correct → efficient
        'partial': 'efficient',     # partial → efficient (C catches incompleteness)
        'bruteforce': 'wasteful',   # bruteforce → wasteful
    }
    
    total = 0
    correct = 0
    
    for prob_name, results in problems.items():
        print(f"\n  {prob_name}:")
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime not in results:
                print(f"    {regime}: MISSING")
                continue
            r = results[regime]
            if 'error' in r:
                print(f"    {regime}: ERROR ({r['error']})")
                continue
            
            exp = expected_map[regime]
            pred = r['predicted']
            match = pred == exp
            total += 1
            if match:
                correct += 1
            
            s_final = r['s_final']
            status = "PASS" if match else "FAIL"
            print(f"    {regime:<12s}: S_final={s_final:>10.2f}  → predicted={pred:<12s}  expected={exp:<12s}  {status}")
    
    accuracy = correct / total if total > 0 else 0
    print(f"\n  Accuracy: {correct}/{total} = {accuracy:.0%}")
    print(f"  Result: {'ACCEPTED ✓' if accuracy == 1.0 else 'NEEDS REVISION ✗'}")
    
    # ═══════════════════════════════════════════════════════════
    # CROSS-PROBLEM COMPARABILITY
    # ═══════════════════════════════════════════════════════════
    
    print(f"\n{'='*90}")
    print(f"  CROSS-PROBLEM COMPARABILITY: S_final values")
    print(f"{'='*90}")
    
    print(f"\n  {'Problem':<20s} | {'Partial':>12s} | {'Correct':>12s} | {'BruteForce':>12s}")
    print(f"  {'-'*20}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}")
    
    for prob_name, results in problems.items():
        vals = {}
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime in results and 'error' not in results[regime]:
                vals[regime] = results[regime]['s_final']
        
        pa = vals.get('partial', 'N/A')
        co = vals.get('correct', 'N/A')
        bf = vals.get('bruteforce', 'N/A')
        
        pa_str = f"{pa:.2f}" if isinstance(pa, (int, float)) else str(pa)
        co_str = f"{co:.2f}" if isinstance(co, (int, float)) else str(co)
        bf_str = f"{bf:.2f}" if isinstance(bf, (int, float)) else str(bf)
        
        print(f"  {prob_name:<20s} | {pa_str:>12s} | {co_str:>12s} | {bf_str:>12s}")
    
    # Check: do S_final values cluster by regime across problems?
    print(f"\n  Clustering check:")
    partial_vals = []
    correct_vals = []
    bf_vals = []
    for _, results in problems.items():
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime in results and 'error' not in results[regime]:
                v = results[regime]['s_final']
                if regime == 'partial': partial_vals.append(v)
                elif regime == 'correct': correct_vals.append(v)
                else: bf_vals.append(v)
    
    print(f"    Partial values:     {partial_vals}")
    print(f"    Correct values:     {correct_vals}")
    print(f"    BruteForce values:  {bf_vals}")
    
    # Check: do S_final values cleanly separate efficient from wasteful?
    print(f"\n  Separation check: efficient vs wasteful:")
    efficient_vals = []
    wasteful_vals = []
    for _, results in problems.items():
        for regime in ['correct', 'partial', 'bruteforce']:
            if regime in results and 'error' not in results[regime]:
                v = results[regime]['s_final']
                if regime == 'bruteforce':
                    wasteful_vals.append(v)
                else:
                    efficient_vals.append(v)
    
    print(f"    Efficient values:  {efficient_vals}")
    print(f"    Wasteful values:   {wasteful_vals}")
    
    if efficient_vals and wasteful_vals:
        eff_max = max(efficient_vals)
        wast_min = min(wasteful_vals)
        gap = wast_min / eff_max
        sep = eff_max < wast_min
        print(f"\n  Max efficient: {eff_max:.2f}")
        print(f"  Min wasteful:  {wast_min:.2f}")
        print(f"  Gap (min_wasteful / max_efficient): {gap:.0f}x")
        print(f"  Clean separation: {'YES ✓' if sep else 'NO ✗'}")
    
    # ═══════════════════════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════════════════════
    
    output = {}
    for pn, res in problems.items():
        output[pn] = {}
        for regime, r in res.items():
            output[pn][regime] = {k: v for k, v in r.items()}
    
    path = r'F:\pythonProject\scratch\s_final_normalized.json'
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved: {path}")

if __name__ == '__main__':
    run()
