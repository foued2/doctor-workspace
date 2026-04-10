from typing import List


class Solution:
    @staticmethod
    def uniquePathsWithObstacles(obstacleGrid: List[List[int]]) -> int:
        # Getting the dimensions of the grid
        n = len(obstacleGrid)
        m = len(obstacleGrid[0])

        # Initializing a 2D list to store the number of unique paths at each cell
        dp = [[0] * m for _ in range(n)]

        # The starting point is always reachable with one path
        dp[0][0] = 1

        # Iterating through each cell of the grid
        for i in range(n):
            for j in range(m):
                # If the current cell is an obstacle, set the number of paths to 0
                if obstacleGrid[i][j] == 1:
                    dp[i][j] = 0
                else:
                    # If the current cell is not an obstacle, the number of paths to reach it
                    # is the sum of the number of paths to reach the cell above it and the cell to its left
                    if i > 0:
                        dp[i][j] += dp[i - 1][j]
                    if j > 0:
                        dp[i][j] += dp[i][j - 1]

        # The result is stored in the bottom-right corner of the grid
        return dp[n - 1][m - 1]


if __name__ == '__main__':
    # Example usage
    print(Solution.uniquePathsWithObstacles(obstacleGrid=[[0, 0, 0], [0, 1, 0], [0, 0, 0]]))
