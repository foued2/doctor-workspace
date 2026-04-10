from typing import List


class Solution:
    @staticmethod
    def satisfiesConditions(grid: List[List[int]]) -> bool:
        # Get the number of rows (m) and columns (n) in the grid
        m = len(grid)
        n = len(grid[0])

        # Iterate through each cell in the grid
        for i in range(m):
            for j in range(n):
                # Check if there is a row below the current cell
                if i + 1 < m:
                    # Ensure the current cell is the same as the cell directly below it
                    if grid[i][j] != grid[i + 1][j]:
                        return False  # Condition failed, return False

                # Check if there is a column to the right of the current cell
                if j + 1 < n:
                    # Ensure the current cell is different from the cell to its right
                    if grid[i][j] == grid[i][j + 1]:
                        return False  # Condition failed, return False

        # If all conditions are satisfied, return True
        return True
