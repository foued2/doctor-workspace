"""
S_FINAL Phase 1 — 10-Problem Generalization Test
=================================================
Tests whether S_final = S_observed / S_ref generalizes beyond curated search problems.

10 problems across 3 categories:
  Non-search (3):     Two Sum, Valid Parentheses, Container With Most Water
  Search/constraint (3): N-Queens (n=8), Word Search, Sudoku Solver
  DP/graph (4):       Longest Common Subsequence, Trapping Rain Water,
                      Climbing Stairs, Number of Islands

Each problem has:
  - S_ref from a canonical (reference) solution
  - correct, partial, and brute-force variants
  - input large enough to expose complexity differences

Outputs:
  1. Separation table (partial < correct < brute?)
  2. Failure modes (where S doesn't separate)
  3. Variance analysis (stability of correct S_final across problems)
"""

import copy
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
# TRACE (same as run_s_final.py)
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
# CLASSIFICATION
# ═══════════════════════════════════════════════════════════

def classify_s_final(s_final):
    if s_final > 1000:
        return 'wasteful'
    else:
        return 'efficient'


# ═══════════════════════════════════════════════════════════
# PROBLEM 1: Two Sum — Hashmap / Array
# S_ref = n (one pass through array, each element recorded once)
# ═══════════════════════════════════════════════════════════

def two_sum_s_ref(n):
    """S_ref = n — one decision per element in optimal hashmap pass."""
    return n

TWO_SUM_INPUT = {
    "nums": [2, 7, 11, 15, 3, 6, 9, 1, 14, 8, 12, 4, 10, 13, 5] * 4,  # 60 elements
    "target": 23
}

def two_sum_correct(nums, target, t):
    """O(n) hashmap — optimal."""
    seen = {}
    for i, n in enumerate(nums):
        t.record(('lookup', i, n))
        complement = target - n
        if complement in seen:
            t.record(('found', seen[complement], i))
            t.record_solution()
            return [seen[complement], i]
        seen[n] = i
    return []

def two_sum_partial(nums, target, t):
    """O(n log n) sort-then-search — sorts first, then two-pointer.
    Extra work from sorting."""
    indexed = [(n, i) for i, n in enumerate(nums)]
    for i in range(len(indexed)):
        t.record(('index', i))
    indexed.sort()
    for i in range(len(indexed)):
        t.record(('sort_step', i))
    left, right = 0, len(indexed) - 1
    while left < right:
        t.record(('two_ptr', left, right))
        s = indexed[left][0] + indexed[right][0]
        if s == target:
            t.record(('found', indexed[left][1], indexed[right][1]))
            t.record_solution()
            return [indexed[left][1], indexed[right][1]]
        elif s < target:
            left += 1
        else:
            right -= 1
    return []

def two_sum_brute(nums, target, t):
    """O(n^2) brute force — every pair."""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            t.record(('check_pair', i, j))
            if nums[i] + nums[j] == target:
                t.record(('found', i, j))
                t.record_solution()
                return [i, j]
    return []


# ═══════════════════════════════════════════════════════════
# PROBLEM 2: Valid Parentheses — Stack / String
# S_ref = len(s) — one character scan
# ═══════════════════════════════════════════════════════════

def vp_s_ref(s):
    """S_ref = len(s) — one pass through the string."""
    return len(s)

VP_INPUT = "({[]})" * 50  # 300 chars

def vp_correct(s, t):
    """O(n) stack — optimal."""
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for i, char in enumerate(s):
        t.record(('char', i, char))
        if char in mapping:
            top = stack.pop() if stack else '#'
            t.record(('pop_check', i, char))
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
            t.record(('push', i, char))
    t.record_solution()
    return not stack

def vp_partial(s, t):
    """Counting approach — incomplete, misses ordering.
    Still O(n) scan but wrong algorithm. S measures efficiency, not correctness."""
    count = {'(': 0, ')': 0, '{': 0, '}': 0, '[': 0, ']': 0}
    for i, c in enumerate(s):
        t.record(('count', i, c))
        count[c] += 1
    t.record_solution()
    return count['('] == count[')'] and count['{'] == count['}'] and count['['] == count[']']

def vp_brute(s, t):
    """Repeatedly remove "()", "{}", "[]" pairs until no change — O(n^2)."""
    prev = ""
    while prev != s:
        t.record(('pass', len(s)))
        prev = s
        for pair in ['()', '{}', '[]']:
            t.record(('replace_check', pair))
            while pair in s:
                t.record(('replace', pair))
                s = s.replace(pair, '', 1)
    t.record_solution()
    return len(s) == 0


# ═══════════════════════════════════════════════════════════
# PROBLEM 3: Container With Most Water — Two Pointers
# S_ref = n — one pass, two pointers converge
# ═══════════════════════════════════════════════════════════

def cw_s_ref(n):
    """S_ref = n — two pointers converge in one pass."""
    return n

CW_INPUT = [1, 8, 6, 2, 5, 4, 8, 3, 7, 2, 9, 1, 7, 3, 6, 4, 8, 2, 5, 9,
            1, 7, 3, 6, 4, 8, 2, 5, 9, 1, 7, 3, 6, 4, 8, 2, 5, 9, 1, 7,
            3, 6, 4, 8, 2, 5, 9, 1, 7, 3]  # 50 elements

def cw_correct(height, t):
    """O(n) two pointers — optimal."""
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        t.record(('pair', left, right))
        h = min(height[left], height[right])
        water = h * (right - left)
        if water > max_water:
            max_water = water
            t.record(('update', left, right, max_water))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    t.record_solution()
    return max_water

def cw_partial(height, t):
    """O(n log n) — sort heights and try top pairs only.
    Misses the width component."""
    indexed = [(h, i) for i, h in enumerate(height)]
    for i in range(len(indexed)):
        t.record(('index', i))
    indexed.sort(reverse=True)
    max_water = 0
    # Only try top-k pairs
    k = min(10, len(indexed))
    for i in range(k):
        for j in range(i + 1, k):
            t.record(('topk_check', i, j))
            h = min(indexed[i][0], indexed[j][0])
            w = abs(indexed[i][1] - indexed[j][1])
            water = h * w
            if water > max_water:
                max_water = water
                t.record(('update', i, j, max_water))
    t.record_solution()
    return max_water

def cw_brute(height, t):
    """O(n^2) — every pair."""
    max_water = 0
    for i in range(len(height)):
        for j in range(i + 1, len(height)):
            t.record(('check', i, j))
            h = min(height[i], height[j])
            water = h * (j - i)
            if water > max_water:
                max_water = water
    t.record_solution()
    return max_water


# ═══════════════════════════════════════════════════════════
# PROBLEM 4: N-Queens (n=8) — Backtracking Search
# S_ref = n — one placement per row in optimal pruning
# ═══════════════════════════════════════════════════════════

def nq_s_ref(n):
    """S_ref = n — one placement per row."""
    return n

def is_valid_nq(board, row, col):
    for r in range(row):
        if board[r] == col or abs(board[r] - col) == abs(r - row):
            return False
    return True

def nq_correct(n, t):
    """Backtracking with diagonal pruning — standard optimal."""
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
    """Finds first solution only — early termination."""
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

def nq_brute(n, t):
    """Generate all n^n placements, validate each."""
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
# PROBLEM 5: Word Search — Grid DFS
# S_ref = len(word) — one character match per position in solution path
# ═══════════════════════════════════════════════════════════

def ws_s_ref(word):
    """S_ref = len(word) — one step per character in exact path."""
    return len(word)

WS_BOARD = [
    ['A','B','C','E'],
    ['S','F','C','S'],
    ['A','D','E','E'],
    ['B','F','C','S'],
    ['A','D','E','E'],
] * 3  # Larger board (15 rows)
# Flatten and restructure to avoid list aliasing
WS_BOARD = [list(row) for row in [['A','B','C','E'],['S','F','C','S'],['A','D','E','E'],['B','F','C','S'],['A','D','E','E']] for _ in range(3)]
WS_WORD = "ABCCED"

def ws_correct(board, word, t):
    """Standard DFS with backtracking on the board."""
    R, C = len(board), len(board[0])
    def dfs(r, c, i):
        t.record(('dfs', r, c, i))
        if i == len(word): t.record_solution(); return True
        if not (0<=r<R and 0<=c<C) or board[r][c] != word[i]: return False
        tmp = board[r][c]; board[r][c] = '#'; t.record(('mark', r, c))
        found = (dfs(r+1,c,i+1) or dfs(r-1,c,i+1) or
                 dfs(r,c+1,i+1) or dfs(r,c-1,i+1))
        board[r][c] = tmp; t.record(('unmark', r, c))
        return found
    for r in range(R):
        for c in range(C):
            if board[r][c] == word[0]:
                if dfs(r, c, 0):
                    return True
    return False

def ws_partial(board, word, t):
    """Only searches from top-left corner, 2 directions only."""
    R, C = len(board), len(board[0])
    def dfs(r, c, i):
        t.record(('dfs', r, c, i))
        if i == len(word): t.record_solution(); return True
        if not (0<=r<R and 0<=c<C) or board[r][c] != word[i]: return False
        tmp = board[r][c]; board[r][c] = '#'; t.record(('mark', r, c))
        found = dfs(r+1,c,i+1) or dfs(r,c+1,i+1)  # only 2 directions
        board[r][c] = tmp; t.record(('unmark', r, c))
        return found
    # Only try first 2 starting positions
    for r in range(min(2, R)):
        for c in range(min(2, C)):
            if board[r][c] == word[0]:
                if dfs(r, c, 0):
                    return True
    return False

def ws_brute(board, word, t):
    """Try all possible paths of length len(word) — exponential."""
    R, C = len(board), len(board[0])
    found = False
    def brute(path, i):
        nonlocal found
        if found:
            return
        if i == len(word):
            t.record(('validate',))
            path_str = ''.join(board[r][c] for r, c in path)
            if path_str == word:
                found = True; t.record_solution()
            return
        for r in range(R):
            for c in range(C):
                t.record(('try', r, c, i))
                if len(path) == 0 or (abs(r-path[-1][0]) + abs(c-path[-1][1]) == 1 and (r,c) not in path):
                    brute(path+[(r,c)], i+1)
    brute([], 0)
    return found


# ═══════════════════════════════════════════════════════════
# PROBLEM 6: Sudoku Solver — Constraint Propagation
# S_ref = empty_cells — one fill decision per empty cell
# ═══════════════════════════════════════════════════════════

SUDOKU_BOARD = [
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

def sd_s_ref(board):
    """S_ref = number of empty cells."""
    return sum(row.count('.') for row in board)

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
    """Backtracking with constraint checking."""
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
    """Depth-limited backtracking — may not complete."""
    b = copy.deepcopy(board)
    def solve(depth=0):
        if depth >= 10:  # depth limit
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

def sudoku_brute(board, t):
    """Try all 9^k combinations for k empty cells (limited to first 10 empties to avoid timeout)."""
    b = copy.deepcopy(board)
    empties = [(i,j) for i in range(9) for j in range(9) if b[i][j]=='.'][:10]
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
# PROBLEM 7: Longest Common Subsequence — DP
# S_ref = m * n — DP table cells to fill
# ═══════════════════════════════════════════════════════════

def lcs_s_ref(m, n):
    """S_ref = m * n — one decision per DP table cell."""
    return m * n

LCS_S1 = "abcde" * 8  # 40 chars
LCS_S2 = "ace" * 13 + "bd"  # 41 chars

def lcs_correct(text1, text2, t):
    """Standard O(m*n) DP table."""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            t.record(('dp', i, j))
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    t.record_solution()
    return dp[m][n]

def lcs_partial(text1, text2, t):
    """Greedy — find matching characters left to right, one pass.
    Misses non-greedy optimal subsequence."""
    m, n = len(text1), len(text2)
    i = 0; j = 0; count = 0
    while i < m and j < n:
        t.record(('greedy', i, j))
        if text1[i] == text2[j]:
            count += 1; t.record(('match', i, j))
            i += 1; j += 1
        else:
            j += 1
    t.record_solution()
    return count

def lcs_brute(text1, text2, t):
    """Recursive with no memoization — O(2^(m+n))."""
    m, n = len(text1), len(text2)
    # Limit depth to avoid infinite recursion on large inputs
    def recurse(i, j, depth=0):
        if depth > 30:  # cap to prevent stack overflow
            t.record(('depth_cap', i, j))
            return 0
        if i == m or j == n:
            t.record(('base', i, j))
            return 0
        t.record(('recurse', i, j))
        if text1[i] == text2[j]:
            return 1 + recurse(i+1, j+1, depth+1)
        else:
            return max(recurse(i+1, j, depth+1), recurse(i, j+1, depth+1))
    t.record_solution()
    return recurse(0, 0)


# ═══════════════════════════════════════════════════════════
# PROBLEM 8: Trapping Rain Water — DP / Two Pointer
# S_ref = n — one pass for each direction
# ═══════════════════════════════════════════════════════════

def trw_s_ref(n):
    """S_ref = n — two passes (left_max + right_max) + one accumulation pass."""
    return n

TRW_INPUT = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1, 0, 2, 1, 0, 3, 1, 0, 2,
             1, 0, 1, 3, 2, 1, 2, 1, 0, 2, 1, 0, 3, 1, 0, 2, 1, 0, 1, 3,
             2, 1, 2, 1, 0, 2, 1, 0, 3, 1]  # 50 elements

def trw_correct(height, t):
    """O(n) DP with left_max and right_max arrays."""
    if not height: return 0
    n = len(height)
    left_max = [0] * n
    right_max = [0] * n
    left_max[0] = height[0]
    for i in range(1, n):
        t.record(('left_max', i))
        left_max[i] = max(left_max[i-1], height[i])
    right_max[n-1] = height[n-1]
    for i in range(n-2, -1, -1):
        t.record(('right_max', i))
        right_max[i] = max(right_max[i+1], height[i])
    total = 0
    for i in range(n):
        t.record(('accumulate', i))
        total += min(left_max[i], right_max[i]) - height[i]
    t.record_solution()
    return total

def trw_partial(height, t):
    """Local max approach — only checks immediate neighbors.
    Wrong algorithm but same O(n) scan."""
    if len(height) < 3: return 0
    total = 0
    for i in range(1, len(height) - 1):
        t.record(('local_check', i))
        local_max = max(height[i-1], height[i+1])
        if height[i] < local_max:
            total += local_max - height[i]
    t.record_solution()
    return total

def trw_brute(height, t):
    """For each position, scan all left and all right to find max — O(n^2)."""
    total = 0
    for i in range(len(height)):
        t.record(('position', i))
        left_max = height[i]
        for j in range(i):
            t.record(('scan_left', i, j))
            left_max = max(left_max, height[j])
        right_max = height[i]
        for j in range(i+1, len(height)):
            t.record(('scan_right', i, j))
            right_max = max(right_max, height[j])
        water = min(left_max, right_max) - height[i]
        if water > 0:
            total += water
    t.record_solution()
    return total


# ═══════════════════════════════════════════════════════════
# PROBLEM 9: Climbing Stairs — Simple DP
# S_ref = n — one step per stair
# ═══════════════════════════════════════════════════════════

def cs_s_ref(n):
    """S_ref = n — one computation per stair."""
    return n

CS_N = 30

def cs_correct(n, t):
    """O(n) DP — optimal."""
    if n <= 2:
        t.record(('base', n)); t.record_solution(); return n
    dp = [0] * (n + 1)
    dp[1] = 1; dp[2] = 2
    for i in range(3, n + 1):
        t.record(('dp', i))
        dp[i] = dp[i-1] + dp[i-2]
    t.record_solution()
    return dp[n]

def cs_partial(n, t):
    """Recursive with no memoization — O(2^n), capped at depth 15."""
    def fib(i, depth=0):
        if depth > 15:
            t.record(('depth_cap', i))
            return 0
        t.record(('recurse', i))
        if i <= 2:
            return i
        return fib(i-1, depth+1) + fib(i-2, depth+1)
    t.record_solution()
    return fib(n)

def cs_brute(n, t):
    """Full recursive tree — O(2^n), capped at depth 20."""
    def fib(i, depth=0):
        if depth > 20:
            t.record(('depth_cap', i))
            return 0
        t.record(('recurse', i))
        if i <= 2:
            return i
        return fib(i-1, depth+1) + fib(i-2, depth+1)
    t.record_solution()
    return fib(n)


# ═══════════════════════════════════════════════════════════
# PROBLEM 10: Number of Islands — Graph BFS/DFS
# S_ref = cells_with_land — one visit per land cell
# ═══════════════════════════════════════════════════════════

def noi_s_ref(grid):
    """S_ref = number of '1' cells — each visited exactly once."""
    return sum(row.count('1') for row in grid)

NOI_GRID = [
    ["1","1","0","0","0"],
    ["1","1","0","0","0"],
    ["0","0","1","0","0"],
    ["0","0","0","1","1"],
] * 5  # 20 rows

def noi_correct(grid, t):
    """DFS — visits each cell once, floods connected components."""
    if not grid: return 0
    R, C = len(grid), len(grid[0])
    count = 0
    def dfs(r, c):
        if not (0<=r<R and 0<=c<C) or grid[r][c] != '1':
            return
        t.record(('visit', r, c))
        grid[r][c] = '0'
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)
    for r in range(R):
        for c in range(C):
            t.record(('scan', r, c))
            if grid[r][c] == '1':
                count += 1; t.record(('island_found', count))
                dfs(r, c)
    t.record_solution()
    return count

def noi_partial(grid, t):
    """Only counts individual land cells, doesn't flood/merge.
    Still visits each cell once."""
    if not grid: return 0
    R, C = len(grid), len(grid[0])
    count = 0
    for r in range(R):
        for c in range(C):
            t.record(('scan', r, c))
            if grid[r][c] == '1':
                count += 1; t.record(('land_cell', r, c))
    t.record_solution()
    return count

def noi_brute(grid, t):
    """For each land cell, do a full BFS to check connectivity — O((R*C)^2)."""
    if not grid: return 0
    R, C = len(grid), len(grid[0])
    count = 0
    visited = set()
    for r in range(R):
        for c in range(C):
            t.record(('scan', r, c))
            if grid[r][c] == '1' and (r,c) not in visited:
                count += 1; t.record(('island_found', count))
                # BFS but record every edge traversal
                queue = [(r, c)]
                while queue:
                    cr, cc = queue.pop(0)
                    if (cr, cc) in visited:
                        continue
                    t.record(('bfs_visit', cr, cc))
                    visited.add((cr, cc))
                    for nr, nc in [(cr+1,cc),(cr-1,cc),(cr,cc+1),(cr,cc-1)]:
                        t.record(('bfs_neighbor', cr, cc, nr, nc))
                        if 0<=nr<R and 0<=nc<C and grid[nr][nc]=='1' and (nr,nc) not in visited:
                            queue.append((nr, nc))
    t.record_solution()
    return count


# ═══════════════════════════════════════════════════════════
# EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════

def run():
    problems = {}
    all_results = []

    # ── 1. Two Sum ──
    ts_sopt = two_sum_s_ref(len(TWO_SUM_INPUT["nums"]))
    print(f"\n{'='*90}")
    print(f"  1. TWO SUM  |  S_ref = {ts_sopt}  (n={len(TWO_SUM_INPUT['nums'])}, hashmap pass)")
    print(f"{'='*90}")
    ts_results = {}
    for label, fn in [
        ('correct',    lambda t: two_sum_correct(TWO_SUM_INPUT["nums"], TWO_SUM_INPUT["target"], t)),
        ('partial',    lambda t: two_sum_partial(TWO_SUM_INPUT["nums"], TWO_SUM_INPUT["target"], t)),
        ('brute',      lambda t: two_sum_brute(TWO_SUM_INPUT["nums"], TWO_SUM_INPUT["target"], t)),
    ]:
        t = Trace(); fn(t)
        s_obs, s_final = t.steps, t.steps / ts_sopt if ts_sopt > 0 else 0
        pred = classify_s_final(s_final)
        ts_results[label] = dict(steps=s_obs, unique=len(t.unique), s_opt=ts_sopt,
                                  s_final=round(s_final, 2), predicted=pred)
        print(f"  {label:<12}: S_obs={s_obs:>10,}  S_ref={ts_sopt:>4}  "
              f"S_final={s_final:>10.2f}  → {pred}")
        all_results.append(("Two Sum", label, s_final, pred))
    problems["Two Sum"] = ts_results

    # ─