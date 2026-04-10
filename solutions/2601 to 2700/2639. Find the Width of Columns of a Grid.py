from typing import List


class Solution:
    @staticmethod
    def findColumnWidth(grid: List[List[int]]) -> List[int]:
        # Determine the number of rows (m) and columns (n) in the grid
        m, n = len(grid), len(grid[0])

        # Initialize a result list to store the maximum width of each column
        res = [0] * n

        # Iterate over each row in the grid
        for i in range(m):
            # Iterate over each column in the grid
            for j in range(n):
                # Convert the current element to a string and find its length
                k = len(str(grid[i][j]))
                # Update the column width if the current element's length is greater
                if k >= res[j]:
                    res[j] = k

        # Return the list of maximum widths for each column
        return res


print(Solution.findColumnWidth(grid=[[-15, 1, 3], [15, 7, 12], [5, 6, -2]]))


class Solution:
    @staticmethod
    def findColumnWidth(grid: List[List[int]]) -> List[int]:
        # Transpose the grid using zip(*grid)
        # zip(*grid) will group elements from each row into columns
        transposed_grid = zip(*grid)

        # Initialize an empty list to store the maximum width of each column
        column_widths = []

        # Iterate over each column in the transposed grid
        for col in transposed_grid:
            # Convert each element in the column to a string and find its length
            # Use map(str, col) to convert each element in the column to a string
            # Use map(len, map(str, col)) to get the length of each string
            # Use max() to find the maximum length in the column
            max_length = max(map(len, map(str, col)))

            # Append the maximum length to the column_widths list
            column_widths.append(max_length)

        # Return the list of maximum widths for each column
        return column_widths


print(Solution.findColumnWidth(grid=[[-15, 1, 3], [15, 7, 12], [5, 6, -2]]))
