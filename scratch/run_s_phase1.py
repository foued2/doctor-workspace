"""
Phase 1 — S_final Generalization Test (10 Problems)
=====================================================
Objective: Test whether S_final generalizes beyond curated search problems.

Problem diversity:
  Non-search (3):     Two Sum, Valid Parentheses, Container With Most Water
  Search/constraint:  N-Queens (n=8), Word Search, Sudoku Solver
  DP/graph (4):       Longest Common Subsequence, Trapping Rain Water,
                      Climbing Stairs, Number of Islands

For each problem:
  - S_ref = total_steps(canonical correct solution)
  - S_final = S_observed / S_ref
  - Run correct, partial, brute variants
  - Check ordering: partial < correct < brute ?

Constraints:
  - At least one large input per problem to expose complexity differences
  - One canonical S_ref per problem (frozen)
"""

import sys
import os
import json
import copy
from collections import defaultdict

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
# PROBLEM 1: Two Sum — HashMap (Non-search)
# S_ref = n (one pass, one record per element)
# Large input: n=1000
# ═══════════════════════════════════════════════════════════

def s_opt_twosum(n):
    """S_opt = n: one lookup per element in optimal single-pass."""
    return n

def twosum_correct(nums, target, t):
    """O(n) hashmap solution."""
    seen = {}
    for i, n in enumerate(nums):
        t.record(('scan', i))
        complement = target - n
        t.record(('lookup', complement))
        if complement in seen:
            t.record(('found', seen[complement], i))
            t.record_solution()
            return [seen[complement], i]
        seen[n] = i
        t.record(('store', n, i))
    return []

def twosum_partial(nums, target, t):
    """O(n log n) sort-based: sort indices by value, then two-pointer."""
    n = len(nums)
    indexed = [(nums[i], i) for i in range(n)]
    for i in range(n):
        t.record(('build', i))
    # Simple insertion sort to keep it instrumented
    for i in range(1, n):
        key = indexed[i]
        j = i - 1
        while j >= 0 and indexed[j][0] > key[0]:
            t.record(('sort_shift', j))
            indexed[j+1] = indexed[j]
            j -= 1
        indexed[j+1] = key
    # Two-pointer
    left, right = 0, n - 1
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

def twosum_brute(nums, target, t):
    """O(n^2) brute force: check all pairs."""
    n = len(nums)
    for i in range(n):
        for j in range(i+1, n):
            t.record(('check', i, j))
            if nums[i] + nums[j] == target:
                t.record(('found', i, j))
                t.record_solution()
                return [i, j]
    return []


# ═══════════════════════════════════════════════════════════
# PROBLEM 2: Valid Parentheses — Stack (Non-search)
# S_ref = len(s) (one char scan)
# Large input: len=500
# ═══════════════════════════════════════════════════════════

def s_opt_valid_parens(s):
    """S_opt = len(s): one character processed."""
    return len(s)

def valid_parens_correct(s, t):
    """O(n) stack-based."""
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for i, char in enumerate(s):
        t.record(('scan', i, char))
        if char in mapping:
            top = stack.pop() if stack else '#'
            t.record(('match', char, top))
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
            t.record(('push', char))
    result = not stack
    if result:
        t.record_solution()
    return result

def valid_parens_partial(s, t):
    """Counting-based: only checks balance, not order."""
    count = {'(': 0, ')': 0, '{': 0, '}': 0, '[': 0, ']': 0}
    for i, c in enumerate(s):
        t.record(('count', i, c))
        count[c] += 1
    result = (count['('] == count[')'] and
              count['{'] == count['}'] and
              count['['] == count[']'])
    if result:
        t.record_solution()
    return result

def valid_parens_brute(s, t):
    """Brute: repeatedly remove "()", "{}", "[]" until stable."""
    t.record(('init', len(s)))
    prev = s
    iterations = 0
    while True:
        t.record(('iteration', iterations))
        prev = s
        s = s.replace('()', '').replace('{}', '').replace('[]', '')
        if s == prev:
            break
        iterations += 1
    result = len(s) == 0
    if result:
        t.record_solution()
    return result


# ═══════════════════════════════════════════════════════════
# PROBLEM 3: Container With Most Water — Two Pointers (Non-search)
# S_ref = n (one pass from both ends)
# Large input: n=500
# ═══════════════════════════════════════════════════════════

def s_opt_container(n):
    """S_opt = n: two-pointer scans each element once."""
    return n

def container_correct(height, t):
    """O(n) two-pointer."""
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        t.record(('probe', left, right))
        h = min(height[left], height[right])
        water = h * (right - left)
        if water > max_water:
            max_water = water
            t.record(('update', left, right, max_water))
        if height[left] < height[right]:
            left += 1
            t.record(('move_left',))
        else:
            right -= 1
            t.record(('move_right',))
    t.record_solution()
    return max_water

def container_partial(height, t):
    """O(n^2) brute but with early pruning (skip smaller heights)."""
    n = len(height)
    max_water = 0
    for i in range(n):
        t.record(('outer', i))
        if height[i] == 0:
            continue
        for j in range(i+1, n):
            t.record(('inner', i, j))
            h = min(height[i], height[j])
            water = h * (j - i)
            if water > max_water:
                max_water = water
    return max_water

def container_brute(height, t):
    """O(n^2) full brute: check every pair, no pruning."""
    n = len(height)
    max_water = 0
    for i in range(n):
        for j in range(i+1, n):
            t.record(('check', i, j))
            h = min(height[i], height[j])
            water = h * (j - i)
            t.record(('compute', i, j, water))
            if water > max_water:
                max_water = water
    return max_water


# ═══════════════════════════════════════════════════════════
# PROBLEM 4: N-Queens (n=8) — Backtracking Search
# S_ref = n = 8
# ═══════════════════════════════════════════════════════════

def s_opt_nqueens(n):
    return n

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
    """Find only first solution, then stop."""
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
# PROBLEM 5: Word Search — Grid DFS
# S_ref = len(word)
# ═══════════════════════════════════════════════════════════

WS_BOARD = [
    ['A','B','C','E'],
    ['S','F','C','S'],
    ['A','D','E','E']
]
WW = "ABCCED"

def s_opt_wordsearch(word):
    return len(word)

def ws_correct(board, word, t):
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
    return any(dfs(r,c,0) for r in range(R) for c in range(C))

def ws_partial(board, word, t):
    """Only search from first row, only right/down directions."""
    R, C = len(board), len(board[0])
    def dfs(r, c, i):
        t.record(('dfs', r, c, i))
        if i == len(word): t.record_solution(); return True
        if not (0<=r<R and 0<=c<C) or board[r][c] != word[i]: return False
        tmp = board[r][c]; board[r][c] = '#'; t.record(('mark', r, c))
        found = dfs(r+1,c,i+1) or dfs(r,c+1,i+1)
        board[r][c] = tmp; t.record(('unmark', r, c))
        return found
    return any(dfs(0,c,0) for c in range(C))

def ws_bruteforce(board, word, t):
    """Try every path without visited tracking."""
    R, C = len(board), len(board[0])
    found = False
    def brute(path, i):
        nonlocal found
        if i == len(word):
            t.record(('validate',))
            formed = ''.join(board[r][c] for r,c in path) if all(0<=r<R and 0<=c<C for r,c in path) else ''
            if formed == word:
                found = True; t.record_solution()
            return
        for r in range(R):
            for c in range(C):
                t.record(('try', r, c, i))
                brute(path+[(r,c)], i+1)
    brute([], 0)
    return found


# ═══════════════════════════════════════════════════════════
# PROBLEM 6: Sudoku Solver — Constraint Propagation
# S_ref = empty_cells
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

def s_opt_sudoku(board):
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
    """Depth-limited to 5 levels."""
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
    """Try all combinations for first 5 empty cells (no constraint checking)."""
    b = copy.deepcopy(board)
    empties = [(i,j) for i in range(9) for j in range(9) if b[i][j]=='.'][:5]
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
# S_ref = m * n (fill DP table once)
# Large input: m=50, n=50
# ═══════════════════════════════════════════════════════════

def s_opt_lcs(m, n):
    """S_opt = m*n: one cell computed per table position."""
    return m * n

def lcs_correct(text1, text2, t):
    """O(m*n) DP."""
    m, n = len(text1), len(text2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            t.record(('cell', i-1, j-1))
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                t.record(('match', i-1, j-1))
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                t.record(('skip', i-1, j-1))
    t.record_solution()
    return dp[m][n]

def lcs_partial(text1, text2, t):
    """Greedy: scan left-to-right, match first occurrence."""
    m, n = len(text1), len(text2)
    count = 0
    j = 0
    for i in range(m):
        t.record(('scan', i))
        while j < n and text2[j] != text1[i]:
            t.record(('skip_b', j))
            j += 1
        if j < n:
            t.record(('match', i, j))
            count += 1
            j += 1
    return count

def lcs_brute(text1, text2, t):
    """Exponential recursion: try all subsequences."""
    def rec(i, j):
        t.record(('recurse', i, j))
        if i < 0 or j < 0:
            return 0
        if text1[i] == text2[j]:
            t.record(('match', i, j))
            return 1 + rec(i-1, j-1)
        else:
            a = rec(i-1, j)
            b = rec(i, j-1)
            t.record(('branch', i, j, a, b))
            return max(a, b)
    return rec(len(text1)-1, len(text2)-1)


# ═══════════════════════════════════════════════════════════
# PROBLEM 8: Trapping Rain Water — DP/Two-Pointer
# S_ref = n (two passes for left_max/right_max, one for total)
# Large input: n=200
# ═══════════════════════════════════════════════════════════

def s_opt_trap(n):
    """S_opt = n: linear scan for precompute + fill."""
    return n

def trap_correct(height, t):
    """O(n) DP: precompute left_max and right_max."""
    if not height:
        return 0
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
        t.record(('fill', i))
        total += min(left_max[i], right_max[i]) - height[i]
    t.record_solution()
    return total

def trap_partial(height, t):
    """Local-max approach: wrong but still scans."""
    if len(height) < 3:
        return 0
    total = 0
    for i in range(1, len(height) - 1):
        t.record(('scan', i))
        local_max = max(height[i-1], height[i+1])
        t.record(('local_max', i, local_max))
        if height[i] < local_max:
            total += local_max - height[i]
    return total

def trap_brute(height, t):
    """For each cell, scan left and right to find max each time."""
    if not height:
        return 0
    n = len(height)
    total = 0
    for i in range(n):
        t.record(('cell', i))
        left_m = height[i]
        for j in range(i):
            t.record(('scan_left', i, j))
            left_m = max(left_m, height[j])
        right_m = height[i]
        for j in range(i+1, n):
            t.record(('scan_right', i, j))
            right_m = max(right_m, height[j])
        water = min(left_m, right_m) - height[i]
        if water > 0:
            total += water
            t.record(('add', i, water))
    return total


# ═══════════════════════════════════════════════════════════
# PROBLEM 9: Climbing Stairs — Simple DP
# S_ref = n (one step computed per stair)
# Large input: n=100
# ═══════════════════════════════════════════════════════════

def s_opt_climb(n):
    return n

def climb_correct(n, t):
    """O(n) DP."""
    if n <= 2:
        t.record(('base', n))
        t.record_solution()
        return n
    dp = [0] * (n + 1)
    dp[1] = 1; dp[2] = 2
    t.record(('init', 1)); t.record(('init', 2))
    for i in range(3, n+1):
        t.record(('compute', i))
        dp[i] = dp[i-1] + dp[i-2]
    t.record_solution()
    return dp[n]

def climb_partial(n, t):
    """Recursive without memoization (exponential but depth-limited)."""
    def rec(k, depth):
        t.record(('recurse', k, depth))
        if depth > 15:
            return 0  # depth limit
        if k <= 2:
            t.record(('base', k))
            return k
        return rec(k-1, depth+1) + rec(k-2, depth+1)
    return rec(n, 0)

def climb_brute(n, t):
    """Pure recursive: 2^n."""
    def rec(k):
        t.record(('recurse', k))
        if k <= 2:
            t.record(('base', k))
            return k
        return rec(k-1) + rec(k-2)
    return rec(n)


# ═══════════════════════════════════════════════════════════
# PROBLEM 10: Number of Islands — Graph BFS/DFS
# S_ref = rows * cols (visit each cell once)
# Large input: 20x20 grid
# ═══════════════════════════════════════════════════════════

def s_opt_islands(grid):
    """S_opt = total cells: each visited once."""
    return len(grid) * len(grid[0])

ISLAND_GRID_20 = [
    ['1','1','0','0','0','1','1','0','0','0','1','0','0','1','1','0','0','0','1','1'],
    ['1','0','0','0','1','1','0','0','1','0','1','0','0','1','0','0','0','1','0','1'],
    ['0','0','1','0','0','0','0','1','1','0','0','1','0','0','0','0','1','0','0','0'],
    ['0','1','1','0','0','0','1','1','0','0','0','0','0','1','1','0','1','1','0','0'],
    ['0','0','0','1','1','0','0','0','0','1','1','1','0','0','0','1','0','0','0','1'],
    ['1','1','0','0','0','0','1','0','0','0','0','0','0','0','1','0','0','1','1','0'],
    ['0','1','0','1','1','0','0','0','1','1','0','0','1','0','0','0','0','0','0','0'],
    ['0','0','0','0','0','1','1','0','0','0','1','0','0','1','0','1','1','0','0','1'],
    ['1','0','1','1','0','0','0','0','1','0','0','0','1','0','0','0','0','1','1','0'],
    ['0','0','0','0','1','1','0','1','0','0','1','1','0','0','1','0','1','0','0','0'],
    ['1','1','0','0','0','0','0','0','0','1','0','0','0','1','0','0','0','0','1','1'],
    ['0','0','1','1','0','0','1','1','0','0','0','0','0','0','0','1','0','0','0','0'],
    ['0','0','0','0','1','0','0','0','0','1','1','0','1','1','0','0','0','1','0','1'],
    ['1','0','1','0','0','0','1','0','1','0','0','0','0','0','1','0','1','0','0','0'],
    ['0','0','0','1','0','1','0','0','0','0','1','1','0','0','0','0','0','0','1','0'],
    ['0','1','0','0','0','0','0','1','1','0','0','0','1','0','1','1','0','1','0','0'],
    ['1','0','0','1','1','0','0','0','0','1','0','1','0','0','0','0','1','0','0','1'],
    ['0','0','1','0','0','1','1','0','0','0','0','0','1','1','0','0','0','0','1','0'],
    ['0','1','0','0','0','0','0','0','1','1','1','0','0','0','0','1','0','1','0','0'],
    ['1','0','0','1','0','0','1','0','0','0','0','1','0','0','1','0','0','0','0','1'],
]

def islands_correct(grid, t):
    """DFS: visit each cell once."""
    if not grid:
        return 0
    R, C = len(grid), len(grid[0])
    count = 0
    def dfs(r, c):
        t.record(('visit', r, c))
        if not (0<=r<R and 0<=c<C) or grid[r][c] != '1':
            return
        grid[r][c] = '0'
        t.record(('mark', r, c))
        dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)
    for r in range(R):
        for c in range(C):
            t.record(('scan', r, c))
            if grid[r][c] == '1':
                count += 1
                t.record(('island_found', r, c))
                dfs(r, c)
    t.record_solution()
    return count

def islands_partial(grid, t):
    """Only scan rows, skip columns (misses connectivity)."""
    if not grid:
        return 0
    R, C = len(grid), len(grid[0])
    count = 0
    for r in range(R):
        t.record(('row_scan', r))
        has_land = False
        for c in range(C):
            t.record(('cell_scan', r, c))
            if grid[r][c] == '1':
                if not has_land:
                    count += 1
                    t.record(('new_component', r, c))
                    has_land = True
    return count

def islands_brute(grid, t):
    """Try every subset of land cells as potential islands."""
    if not grid:
        return 0
    R, C = len(grid), len(grid[0])
    land_cells = [(r,c) for r in range(R) for c in range(C) if grid[r][c]=='1']
    t.record(('land_count', len(land_cells)))
    # Exponential: try all subsets (capped at 12 for feasibility)
    cap = min(len(land_cells), 12)
    count = 0
    def try_subset(idx, current):
        nonlocal count
        if idx == cap:
            t.record(('validate_subset', len(current)))
            if current:
                count += 1
                t.record_solution()
            return
        # Include
        current.append(land_cells[idx])
        t.record(('include', idx))
        try_subset(idx+1, current)
        current.pop()
        # Exclude
        t.record(('exclude', idx))
        try_subset(idx+1, current)
    try_subset(0, [])
    return count


# ═══════════════════════════════════════════════════════════
# EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════

def run():
    results = {}
    separation_table = []
    failure_modes = []
    variance_analysis = {'correct_s_final': [], 'partial_s_final': [], 'brute_s_final': []}

    # ─── Problem 1: Two Sum ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 1: Two Sum (n=1000) | S_ref = 1000 (one pass)")
    print(f"{'='*90}")
    nums_large = list(range(1, 1001))  # [1,2,...,1000]
    target_large = 1999  # 999 + 1000
    s_ref = s_opt_twosum(1000)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: twosum_correct(nums_large, target_large, t)),
        ('partial',  lambda t: twosum_partial(nums_large, target_large, t)),
        ('brute',    lambda t: twosum_brute(nums_large, target_large, t)),
    ]:
        t = Trace()
        result = fn(t)
        s_obs = t.steps
        s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
        pred = classify_s_final(s_final)
        prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                               'predicted': pred, 'unique': len(t.unique)}
        print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
              f"S_final={s_final:>10.2f}  → {pred}")
        variance_analysis[f'{label}_s_final'].append(s_final)
    results['Two Sum'] = prob_results
    separation_table.append({
        'problem': 'Two Sum', 'category': 'non-search',
        'partial': prob_results['partial']['s_final'],
        'correct': prob_results['correct']['s_final'],
        'brute': prob_results['brute']['s_final'],
    })

    # ─── Problem 2: Valid Parentheses ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 2: Valid Parentheses (len=500) | S_ref = 500")
    print(f"{'='*90}")
    s_parens = "()" * 250  # 500 chars, valid
    s_ref = s_opt_valid_parens(s_parens)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: valid_parens_correct(s_parens, t)),
        ('partial',  lambda t: valid_parens_partial(s_parens, t)),
        ('brute',    lambda t: valid_parens_brute(s_parens, t)),
    ]:
        t = Trace()
        result = fn(t)
        s_obs = t.steps
        s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
        pred = classify_s_final(s_final)
        prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                               'predicted': pred, 'unique': len(t.unique)}
        print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
              f"S_final={s_final:>10.2f}  → {pred}")
        variance_analysis[f'{label}_s_final'].append(s_final)
    results['Valid Parentheses'] = prob_results
    separation_table.append({
        'problem': 'Valid Parentheses', 'category': 'non-search',
        'partial': prob_results['partial']['s_final'],
        'correct': prob_results['correct']['s_final'],
        'brute': prob_results['brute']['s_final'],
    })

    # ─── Problem 3: Container With Most Water ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 3: Container (n=500) | S_ref = 500")
    print(f"{'='*90}")
    height_large = list(range(1, 501))  # [1,2,...,500]
    s_ref = s_opt_container(500)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: container_correct(height_large, t)),
        ('partial',  lambda t: container_partial(height_large, t)),
        ('brute',    lambda t: container_brute(height_large, t)),
    ]:
        t = Trace()
        result = fn(t)
        s_obs = t.steps
        s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
        pred = classify_s_final(s_final)
        prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                               'predicted': pred, 'unique': len(t.unique)}
        print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
              f"S_final={s_final:>10.2f}  → {pred}")
        variance_analysis[f'{label}_s_final'].append(s_final)
    results['Container'] = prob_results
    separation_table.append({
        'problem': 'Container', 'category': 'non-search',
        'partial': prob_results['partial']['s_final'],
        'correct': prob_results['correct']['s_final'],
        'brute': prob_results['brute']['s_final'],
    })

    # ─── Problem 4: N-Queens (n=8) ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 4: N-Queens (n=8) | S_ref = 8")
    print(f"{'='*90}")
    s_ref = s_opt_nqueens(8)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: nq_correct(8, t)),
        ('partial',  lambda t: nq_partial(8, t)),
        ('brute',    lambda t: nq_bruteforce(8, t)),
    ]:
        t = Trace()
        result = fn(t)
        s_obs = t.steps
        s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
        pred = classify_s_final(s_final)
        prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                               'predicted': pred, 'unique': len(t.unique),
                               'solutions': t.solutions}
        print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
              f"S_final={s_final:>10.2f}  → {pred}  (sols={t.solutions})")
        variance_analysis[f'{label}_s_final'].append(s_final)
    results['N-Queens (n=8)'] = prob_results
    separation_table.append({
        'problem': 'N-Queens (n=8)', 'category': 'search',
        'partial': prob_results['partial']['s_final'],
        'correct': prob_results['correct']['s_final'],
        'brute': prob_results['brute']['s_final'],
    })

    # ─── Problem 5: Word Search ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 5: Word Search (len='{WW}') | S_ref = {len(WW)}")
    print(f"{'='*90}")
    s_ref = s_opt_wordsearch(WW)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: ws_correct(copy.deepcopy(WS_BOARD), WW, t)),
        ('partial',  lambda t: ws_partial(copy.deepcopy(WS_BOARD), WW, t)),
        ('brute',    lambda t: ws_bruteforce(copy.deepcopy(WS_BOARD), WW, t)),
    ]:
        t = Trace()
        try:
            result = fn(t)
            s_obs = t.steps
            s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
            pred = classify_s_final(s_final)
            prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                                   'predicted': pred, 'unique': len(t.unique)}
            print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
                  f"S_final={s_final:>10.2f}  → {pred}")
            variance_analysis[f'{label}_s_final'].append(s_final)
        except RecursionError:
            prob_results[label] = {'error': 'RecursionError', 's_final': float('inf'),
                                   'predicted': 'wasteful'}
            print(f"  {label:<10}: RecursionError → wasteful")
            variance_analysis[f'{label}_s_final'].append(999999)
    results['Word Search'] = prob_results
    separation_table.append({
        'problem': 'Word Search', 'category': 'search',
        'partial': prob_results['partial'].get('s_final', float('inf')),
        'correct': prob_results['correct'].get('s_final', float('inf')),
        'brute': prob_results['brute'].get('s_final', float('inf')),
    })

    # ─── Problem 6: Sudoku ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 6: Sudoku | S_ref = {s_opt_sudoku(SUDOKU)} (empty cells)")
    print(f"{'='*90}")
    s_ref = s_opt_sudoku(SUDOKU)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: sudoku_correct(copy.deepcopy(SUDOKU), t)),
        ('partial',  lambda t: sudoku_partial(copy.deepcopy(SUDOKU), t)),
        ('brute',    lambda t: sudoku_bruteforce(copy.deepcopy(SUDOKU), t)),
    ]:
        t = Trace()
        try:
            result = fn(t)
            s_obs = t.steps
            s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
            pred = classify_s_final(s_final)
            prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                                   'predicted': pred, 'unique': len(t.unique)}
            print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
                  f"S_final={s_final:>10.2f}  → {pred}")
            variance_analysis[f'{label}_s_final'].append(s_final)
        except RecursionError:
            prob_results[label] = {'error': 'RecursionError', 's_final': float('inf'),
                                   'predicted': 'wasteful'}
            print(f"  {label:<10}: RecursionError → wasteful")
            variance_analysis[f'{label}_s_final'].append(999999)
    results['Sudoku'] = prob_results
    separation_table.append({
        'problem': 'Sudoku', 'category': 'search',
        'partial': prob_results['partial'].get('s_final', float('inf')),
        'correct': prob_results['correct'].get('s_final', float('inf')),
        'brute': prob_results['brute'].get('s_final', float('inf')),
    })

    # ─── Problem 7: LCS ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 7: LCS (m=15, n=15) | S_ref = 225 (DP table)")
    print(f"{'='*90}")
    text1_15 = "abcdefabcdeabcd"   # 15 chars
    text2_15 = "abcxyzabcxyzabc"   # 15 chars
    s_ref = s_opt_lcs(15, 15)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: lcs_correct(text1_15, text2_15, t)),
        ('partial',  lambda t: lcs_partial(text1_15, text2_15, t)),
        ('brute',    lambda t: lcs_brute(text1_15, text2_15, t)),
    ]:
        t = Trace()
        try:
            result = fn(t)
            s_obs = t.steps
            s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
            pred = classify_s_final(s_final)
            prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                                   'predicted': pred, 'unique': len(t.unique)}
            print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
                  f"S_final={s_final:>10.2f}  → {pred}")
            variance_analysis[f'{label}_s_final'].append(s_final)
        except RecursionError:
            prob_results[label] = {'error': 'RecursionError', 's_final': float('inf'),
                                   'predicted': 'wasteful'}
            print(f"  {label:<10}: RecursionError → wasteful")
            variance_analysis[f'{label}_s_final'].append(999999)
    results['LCS (50x50)'] = prob_results
    separation_table.append({
        'problem': 'LCS (50x50)', 'category': 'dp',
        'partial': prob_results['partial'].get('s_final', float('inf')),
        'correct': prob_results['correct'].get('s_final', float('inf')),
        'brute': prob_results['brute'].get('s_final', float('inf')),
    })

    # ─── Problem 8: Trapping Rain Water ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 8: Trapping Rain Water (n=200) | S_ref = 200")
    print(f"{'='*90}")
    height_trap = [i % 10 for i in range(200)]  # repeating [0,1,2,...,9,0,1,...]
    s_ref = s_opt_trap(200)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: trap_correct(height_trap, t)),
        ('partial',  lambda t: trap_partial(height_trap, t)),
        ('brute',    lambda t: trap_brute(height_trap, t)),
    ]:
        t = Trace()
        result = fn(t)
        s_obs = t.steps
        s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
        pred = classify_s_final(s_final)
        prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                               'predicted': pred, 'unique': len(t.unique)}
        print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
              f"S_final={s_final:>10.2f}  → {pred}")
        variance_analysis[f'{label}_s_final'].append(s_final)
    results['Trap Water (n=200)'] = prob_results
    separation_table.append({
        'problem': 'Trap Water (n=200)', 'category': 'dp',
        'partial': prob_results['partial']['s_final'],
        'correct': prob_results['correct']['s_final'],
        'brute': prob_results['brute']['s_final'],
    })

    # ─── Problem 9: Climbing Stairs ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 9: Climbing Stairs (n=20) | S_ref = 20")
    print(f"{'='*90}")
    # Using n=20 for brute feasibility (2^20 ~ 1M, manageable)
    climb_n = 20
    s_ref = s_opt_climb(climb_n)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: climb_correct(climb_n, t)),
        ('partial',  lambda t: climb_partial(climb_n, t)),
        ('brute',    lambda t: climb_brute(climb_n, t)),
    ]:
        t = Trace()
        try:
            result = fn(t)
            s_obs = t.steps
            s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
            pred = classify_s_final(s_final)
            prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                                   'predicted': pred, 'unique': len(t.unique)}
            print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
                  f"S_final={s_final:>10.2f}  → {pred}")
            variance_analysis[f'{label}_s_final'].append(s_final)
        except RecursionError:
            prob_results[label] = {'error': 'RecursionError', 's_final': float('inf'),
                                   'predicted': 'wasteful'}
            print(f"  {label:<10}: RecursionError → wasteful")
            variance_analysis[f'{label}_s_final'].append(999999)
    results[f'Climbing Stairs (n={climb_n})'] = prob_results
    separation_table.append({
        'problem': f'Climbing Stairs (n={climb_n})', 'category': 'dp',
        'partial': prob_results['partial'].get('s_final', float('inf')),
        'correct': prob_results['correct'].get('s_final', float('inf')),
        'brute': prob_results['brute'].get('s_final', float('inf')),
    })

    # ─── Problem 10: Number of Islands ───
    print(f"\n{'='*90}")
    print(f"  PROBLEM 10: Number of Islands (20x20) | S_ref = 400")
    print(f"{'='*90}")
    s_ref = s_opt_islands(ISLAND_GRID_20)
    prob_results = {}
    for label, fn in [
        ('correct',  lambda t: islands_correct(copy.deepcopy(ISLAND_GRID_20), t)),
        ('partial',  lambda t: islands_partial(copy.deepcopy(ISLAND_GRID_20), t)),
        ('brute',    lambda t: islands_brute(copy.deepcopy(ISLAND_GRID_20), t)),
    ]:
        t = Trace()
        try:
            result = fn(t)
            s_obs = t.steps
            s_final = round(s_obs / s_ref, 2) if s_ref > 0 else 0
            pred = classify_s_final(s_final)
            prob_results[label] = {'s_obs': s_obs, 's_ref': s_ref, 's_final': s_final,
                                   'predicted': pred, 'unique': len(t.unique)}
            print(f"  {label:<10}: S_obs={s_obs:>10,}  S_ref={s_ref:>6}  "
                  f"S_final={s_final:>10.2f}  → {pred}")
            variance_analysis[f'{label}_s_final'].append(s_final)
        except RecursionError:
            prob_results[label] = {'error': 'RecursionError', 's_final': float('inf'),
                                   'predicted': 'wasteful'}
            print(f"  {label:<10}: RecursionError → wasteful")
            variance_analysis[f'{label}_s_final'].append(999999)
    results['Islands (20x20)'] = prob_results
    separation_table.append({
        'problem': 'Islands (20x20)', 'category': 'graph',
        'partial': prob_results['partial'].get('s_final', float('inf')),
        'correct': prob_results['correct'].get('s_final', float('inf')),
        'brute': prob_results['brute'].get('s_final', float('inf')),
    })

    # ═══════════════════════════════════════════════════════════
    # ANALYSIS OUTPUTS
    # ═══════════════════════════════════════════════════════════

    # 1. Separation Table
    print(f"\n{'='*90}")
    print(f"  SEPARATION TABLE: partial < correct < brute?")
    print(f"{'='*90}")
    print(f"\n  {'Problem':<25s} | {'Category':<10s} | {'Partial':>10s} | {'Correct':>10s} | {'Brute':>12s} | Ordering?")
    print(f"  {'-'*25}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*12}")

    ordering_passes = 0
    ordering_total = 0
    for row in separation_table:
        p, c, b = row['partial'], row['correct'], row['brute']
        inf_val = float('inf')
        # Check ordering: partial < correct < brute
        if p == inf_val or c == inf_val or b == inf_val:
            ordering = "N/A (overflow)"
        elif p < c < b:
            ordering = "PASS ✓"
            ordering_passes += 1
            ordering_total += 1
        else:
            ordering = f"FAIL ✗ ({p} vs {c} vs {b})"
            ordering_total += 1

        p_str = f"{p:.2f}" if p != inf_val else "INF"
        c_str = f"{c:.2f}" if c != inf_val else "INF"
        b_str = f"{b:.2f}" if b != inf_val else "INF"
        print(f"  {row['problem']:<25s} | {row['category']:<10s} | {p_str:>10s} | {c_str:>10s} | {b_str:>12s} | {ordering}")

    # 2. Failure Modes
    print(f"\n{'='*90}")
    print(f"  FAILURE MODES")
    print(f"{'='*90}")
    for row in separation_table:
        p, c, b = row['partial'], row['correct'], row['brute']
        inf_val = float('inf')
        modes = []
        if c != inf_val and b != inf_val and c >= b * 0.5:
            modes.append("correct ≈ brute (insufficient separation)")
        if p != inf_val and c != inf_val and abs(p - c) / max(c, 1) < 0.1:
            modes.append("partial ≈ correct (can't distinguish)")
        if b != inf_val and b < 1000:
            modes.append("brute NOT classified as wasteful (threshold too high)")
        if c != inf_val and c > 1000:
            modes.append("correct classified as wasteful (threshold too low)")
        if modes:
            print(f"  ⚠ {row['problem']} ({row['category']}):")
            for m in modes:
                print(f"    - {m}")
            failure_modes.append({'problem': row['problem'], 'category': row['category'], 'modes': modes})
        else:
            print(f"  ✓ {row['problem']} ({row['category']}): No failure modes")

    # 3. Variance Analysis
    print(f"\n{'='*90}")
    print(f"  VARIANCE ANALYSIS")
    print(f"{'='*90}")
    for regime in ['correct_s_final', 'partial_s_final', 'brute_s_final']:
        vals = [v for v in variance_analysis[regime] if v < 999999]
        if not vals:
            print(f"  {regime}: No finite values")
            continue
        mean_v = sum(vals) / len(vals)
        min_v = min(vals)
        max_v = max(vals)
        cv = (max_v - min_v) / mean_v if mean_v > 0 else 0
        stable = cv < 1.0
        print(f"  {regime}:")
        print(f"    mean={mean_v:.2f}  min={min_v:.2f}  max={max_v:.2f}  "
              f"CV={cv:.2f}  stable={'YES ✓' if stable else 'NO ✗ (high variance)'}")
        print(f"    values: {[round(v, 2) for v in vals]}")

    # ═══════════════════════════════════════════════════════════
    # DECISION
    # ═══════════════════════════════════════════════════════════

    print(f"\n{'='*90}")
    print(f"  PHASE 1 DECISION")
    print(f"{'='*90}")

    # Count categories that pass
    cat_results = defaultdict(lambda: {'total': 0, 'pass': 0})
    for row in separation_table:
        p, c, b = row['partial'], row['correct'], row['brute']
        inf_val = float('inf')
        cat_results[row['category']]['total'] += 1
        if p != inf_val and c != inf_val and b != inf_val and p < c < b:
            cat_results[row['category']]['pass'] += 1

    for cat, res in cat_results.items():
        rate = res['pass'] / res['total'] if res['total'] > 0 else 0
        print(f"  {cat}: {res['pass']}/{res['total']} pass ({rate:.0%})")

    # Overall verdict
    total_pass = sum(r['pass'] for r in cat_results.values())
    total_problems = sum(r['total'] for r in cat_results.values())
    overall_rate = total_pass / total_problems if total_problems > 0 else 0

    if overall_rate >= 0.8:
        verdict = "CASE A — S generalizes across domains. Proceed to 30-50 problems."
    elif overall_rate >= 0.4:
        verdict = "CASE B — S partially works. Strong in some domains, weak in others. S becomes conditional dimension."
    else:
        verdict = "CASE C — S fails. No consistent separation. Stays as diagnostic tool only."

    print(f"\n  Overall: {total_pass}/{total_problems} pass ({overall_rate:.0%})")
    print(f"  → {verdict}")

    # ═══════════════════════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════════════════════

    output = {
        'results': {},
        'separation_table': separation_table,
        'failure_modes': failure_modes,
        'variance_analysis': {},
        'decision': {
            'category_results': {k: dict(v) for k, v in cat_results.items()},
            'total_pass': total_pass,
            'total_problems': total_problems,
            'overall_rate': round(overall_rate, 2),
            'verdict': verdict,
        }
    }

    # Convert results to serializable
    for prob_name, prob_res in results.items():
        output['results'][prob_name] = {}
        for regime, r in prob_res.items():
            output['results'][prob_name][regime] = {k: v for k, v in r.items()}

    for regime, vals in variance_analysis.items():
        output['variance_analysis'][regime] = [round(v, 2) for v in vals]

    path = r'F:\pythonProject\scratch\s_phase1_results.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved: {path}")


if __name__ == '__main__':
    run()
