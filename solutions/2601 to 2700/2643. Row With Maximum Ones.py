from typing import List


class Solution:
    @staticmethod
    def rowAndMaximumOnes(mat: List[List[int]]) -> List[int]:
        """
        matrix
        """
        # Initialize variables to store the maximum number of ones and its corresponding row index
        max_ones_count = 0
        max_ones_row = 0

        # Iterate over each row of the matrix
        for i, row in enumerate(mat):
            # Calculate the number of ones in the current row
            ones_count = sum(row)
            # Update the maximum number of ones and its corresponding row index if a new maximum is found
            if ones_count > max_ones_count:
                max_ones_count = ones_count
                max_ones_row = i

        # Return a list containing the row index with the maximum number of ones and the maximum number of ones in
        # that row
        return [max_ones_row, max_ones_count]


print(Solution.rowAndMaximumOnes(mat=[[0, 0, 0], [0, 1, 1]]))
