from typing import List


class Solution:
    @staticmethod
    def equalPairs(grid: List[List[int]]) -> int:
        ans = 0

        # Create a dictionary to count the frequency of each row
        row_count = {}
        for row in grid:
            row_tuple = tuple(row)
            if row_tuple in row_count:
                row_count[row_tuple] += 1
            else:
                row_count[row_tuple] = 1

        # Create a dictionary to count the frequency of each column
        col_count = {}
        for col in zip(*grid):
            col_tuple = tuple(col)
            if col_tuple in col_count:
                col_count[col_tuple] += 1
            else:
                col_count[col_tuple] = 1

        # Count the number of matching rows and columns
        for row_tuple in row_count:
            if row_tuple in col_count:
                ans += row_count[row_tuple] * col_count[row_tuple]

        return ans


# Example usage
grid = [
    [3, 2, 1],
    [1, 7, 6],
    [2, 7, 7]
]
print(Solution.equalPairs(grid))  # Output: 1

print(Solution.equalPairs(grid=[[3, 1, 2, 2], [1, 4, 4, 5], [2, 4, 2, 2], [2, 4, 2, 2]]))


class Solution:
    @staticmethod
    def equalPairs(grid: List[List[int]]) -> int:
        ans = 0

        # Transpose the grid to get columns
        transposed_grid = list(zip(*grid))

        # Iterate through each row and each column
        for row in grid:
            for col in transposed_grid:
                # Check if the row and column are exactly equal
                if list(row) == list(col):
                    ans += 1

        return ans


# Example usage
grid = [
    [3, 2, 1],
    [1, 7, 6],
    [2, 7, 7]
]
print(Solution.equalPairs(grid))  # Output: 1
