"""Debug N-Queens correct solution output for each test case."""
code = """def solveNQueens(n):
    results = []
    def backtrack(row, cols, diag1, diag2, board):
        if row == n:
            results.append([''.join(r) for r in board])
            return
        for col in range(n):
            d1 = row - col
            d2 = row + col
            if col in cols or d1 in diag1 or d2 in diag2:
                continue
            cols.add(col)
            diag1.add(d1)
            diag2.add(d2)
            board[row][col] = 'Q'
            backtrack(row + 1, cols, diag1, diag2, board)
            board[row][col] = '.'
            cols.remove(col)
            diag1.remove(d1)
            diag2.remove(d2)
    board = [['.'] * n for _ in range(n)]
    backtrack(0, set(), set(), set(), board)
    return results"""

ns = {}
exec(code, ns)
f = ns['solveNQueens']

r1 = f(1)
r4 = f(4)
r0 = f(0)

with open(r'F:\pythonProject\scratch\nqueens_debug_out.txt', 'w') as out:
    out.write(f"n=1: count={len(r1)} expected=1 PASS={len(r1)==1}\n")
    out.write(f"n=4: count={len(r4)} expected=2 PASS={len(r4)==2}\n")
    out.write(f"n=0: count={len(r0)} expected=0 PASS={len(r0)==0}\n")
    out.write(f"n=0 result: {r0}\n")
print('done')
