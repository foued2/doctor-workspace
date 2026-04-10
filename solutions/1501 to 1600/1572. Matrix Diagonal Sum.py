from typing import List


class Solution:
    @staticmethod
    def diagonalSum(mat: List[List[int]]) -> int:
        # Get the size of the matrix
        n = len(mat)

        # Calculate the middle index for the center element
        mid = n // 2

        # Initialize the sum of the diagonals
        summation = 0

        # Iterate through each row of the matrix
        for i in range(n):
            # Add the element from the primary diagonal
            summation += mat[i][i]

            # Add the element from the secondary diagonal
            summation += mat[i][n - 1 - i]

        # If the matrix has an odd size, subtract the middle element once
        # because it has been added twice (once in each diagonal)
        if n % 2 == 1:
            summation -= mat[mid][mid]

        # Return the final sum of the diagonals
        return summation


print(Solution.diagonalSum(mat=[[1, 1, 1, 1],
                                [1, 1, 1, 1],
                                [1, 1, 1, 1],
                                [1, 1, 1, 1]]))
