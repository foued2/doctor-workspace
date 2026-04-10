from typing import List


class Solution:
    @staticmethod
    def largestLocal(grid: List[List[int]]) -> List[List[int]]:
        # Initialize the result list to store the largest values from each 3x3 subgrid.
        res = []

        # Get the size of the grid (assuming it's a square grid).
        n = len(grid)

        # Iterate through each starting row index for the 3x3 sub-grids.
        for k in range(n - 2):
            # Initialize a list to store the largest values for the current row of 3x3 sub-grids.
            row = []

            # Iterate through each starting column index for the 3x3 sub-grids.
            for m in range(n - 2):
                # Initialize the largest value found in the current 3x3 subgrid.
                largest = 0

                # Iterate through the 3 rows of the current 3x3 subgrid.
                for i in range(3):
                    # Iterate through the 3 columns of the current 3x3 subgrid.
                    for j in range(3):
                        # Update the largest value if the current grid value is greater.
                        largest = max(largest, grid[k + i][m + j])

                # Append the largest value found in the current 3x3 subgrid to the row list.
                row.append(largest)

            # Append the row of largest values to the result list.
            res.append(row)

        # Return the result list containing the largest values from each 3x3 subgrid.
        return res


print(Solution.largestLocal(grid=[[9, 9, 8, 1], [5, 6, 2, 6], [8, 2, 6, 4], [6, 2, 2, 2]]))
