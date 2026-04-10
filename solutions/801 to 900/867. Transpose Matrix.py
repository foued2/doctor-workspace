from typing import List


class Solution:
    @staticmethod
    def transpose(matrix: List[List[int]]) -> List[List[int]]:
        # Get the number of rows and columns in the original matrix
        num_rows, num_cols = len(matrix), len(matrix[0])

        # Initialize a new matrix to store the transposed result
        transposed_matrix = [[0] * num_rows for _ in range(num_cols)]

        # Iterate over each element in the original matrix
        for row_index in range(num_rows):
            for col_index in range(num_cols):
                # Transpose the element to the new matrix
                transposed_matrix[col_index][row_index] = matrix[row_index][col_index]

        # Return the transposed matrix
        return transposed_matrix


print(Solution.transpose(matrix=[[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
