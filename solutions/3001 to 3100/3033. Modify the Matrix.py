from typing import List


class Solution:
    @staticmethod
    def modifiedMatrix(matrix: List[List[int]]) -> List[List[int]]:
        # Get the number of rows and columns in the matrix
        n = len(matrix)
        m = len(matrix[0])

        # Create a copy of the original matrix to store the modified values
        answer = [row[:] for row in matrix]

        # Iterate through each cell in the matrix
        for i in range(n):
            for j in range(m):
                # Check if the current cell value is -1
                if matrix[i][j] == -1:
                    # If the current cell is -1, replace it with the maximum value in the same column
                    max_val = max(matrix[k][j] for k in range(n))
                    answer[i][j] = max_val

        # Return the modified matrix
        return answer


# Test the function with a sample matrix
print(Solution.modifiedMatrix(matrix=[[1, 2, -1], [4, -1, 6], [7, 8, 9]]))
