from typing import List


class Solution:
    @staticmethod
    def maxSum(grid: List[List[int]]) -> int:
        # Initialize the variable to store the maximum hourglass sum
        ans = 0

        # Get the number of rows (m) and columns (n) in the grid
        m, n = len(grid), len(grid[0])

        # Iterate over the grid to find all possible hourglasses
        # We stop at m-2 and n-2 because an hourglass requires 3 rows and 3 columns
        for i in range(m - 2):
            for j in range(n - 2):
                # Calculate the sum of the current hourglass
                # The hourglass consists of:
                #   - The top 3 elements: grid[i][j] + grid[i][j+1] + grid[i][j+2]
                #   - The middle element: grid[i+1][j+1]
                #   - The bottom 3 elements: grid[i+2][j] + grid[i+2][j+1] + grid[i+2][j+2]
                hourglass = (
                        sum(grid[i][j: j + 3])  # Top 3 elements
                        + grid[i + 1][j + 1]  # Middle element
                        + sum(grid[i + 2][j: j + 3])  # Bottom 3 elements
                )

                # Update the maximum hourglass sum if the current one is greater
                ans = max(ans, hourglass)

        # Return the maximum hourglass sum found
        return ans


print(Solution.maxSum(grid=[[6, 2, 1, 3], [4, 2, 1, 5], [9, 2, 8, 7], [4, 1, 2, 9]]))
