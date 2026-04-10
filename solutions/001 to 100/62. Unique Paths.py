class Solution:
    @staticmethod
    def uniquePaths(m: int, n: int) -> int:
        # Initializing a 2D list to store the number of unique paths at each cell
        dp = [[0] * m for _ in range(n)]

        # The starting point is always reachable with one path
        dp[0][0] = 1

        # Iterating through each cell of the grid
        for i in range(n):
            for j in range(m):
                if i > 0:
                    dp[i][j] += dp[i - 1][j]
                if j > 0:
                    dp[i][j] += dp[i][j - 1]

        # The result is stored in the bottom-right corner of the grid
        return dp[n - 1][m - 1]


if __name__ == '__main__':
    # Example usage
    print(Solution.uniquePaths(m=3, n=7))
