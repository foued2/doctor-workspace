from typing import List


class Solution:
    @staticmethod
    def countSubmatrices(grid: List[List[int]], k: int) -> int:
        n = len(grid[0])
        m = len(grid)
        i, j = 0, 0
        while i <= n and j <= m:
            sub = [[0 for _ in range(j + 1)] for _ in range(i + 1)]
            # s = sum(sub)
            for a in range(i):
                for b in range(j):
                    sub[a][b] = grid[a][b]
            print(sub)
            j += 1
            i += 1
        return n

    print(countSubmatrices(grid=[[7, 6, 3], [6, 6, 1]], k=18))
