from typing import List


class Solution:
    @staticmethod
    def findPeakGrid(mat: List[List[int]]) -> List[int]:
        def find_max_in_column(column):
            # Iterate over each row in the specified column
            max_row = 0
            for i in range(len(mat)):
                # Update max_row if a larger element is found
                if mat[i][column] > mat[max_row][column]:
                    max_row = i
            return max_row

        left, right = 0, len(mat[0]) - 1

        while left <= right:
            mid_col = (left + right) // 2  # Calculate middle column index
            max_row = find_max_in_column(mid_col)

            # Determine the direction of search based on neighboring columns
            if mid_col > 0 and mat[max_row][mid_col] < mat[max_row][mid_col - 1]:
                right = mid_col - 1  # Move search space to the left
            elif mid_col < len(mat[0]) - 1 and mat[max_row][mid_col] < mat[max_row][mid_col + 1]:
                left = mid_col + 1  # Move search space to the right
            else:
                return [max_row, mid_col]  # Found a peak element


if __name__ == '__main__':
    print(Solution.findPeakGrid(mat=[[10, 20, 15], [21, 30, 14], [7, 16, 32]]))
