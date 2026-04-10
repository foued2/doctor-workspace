from typing import List


class Solution:
    @staticmethod
    def checkXMatrix(grid: List[List[int]]) -> bool:
        # Get the size of the grid (assuming it's a square matrix)
        n = len(grid)

        # Traverse through each cell of the grid
        for i in range(n):
            for j in range(n):
                # Check the diagonal cells
                if i == j:  # If it's on the main diagonal
                    # If the value is not 0, it's not an X-matrix
                    if grid[i][j] == 0:
                        return False
                elif n - (i + 1) == j:  # If it's on the opposite diagonal
                    # If the value is not 0, it's not an X-matrix
                    if grid[i][j] == 0:
                        return False
                else:  # For other cells
                    # If any other cell is not 0, it's not an X-matrix
                    if grid[i][j] != 0:
                        return False

        # If all conditions pass, it's an X-matrix
        return True


print(Solution.checkXMatrix(grid=[[5, 7, 0], [0, 3, 1], [0, 5, 0]]))
