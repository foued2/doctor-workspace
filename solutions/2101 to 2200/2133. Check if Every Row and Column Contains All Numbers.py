from typing import List


class Solution:
    @staticmethod
    def checkValid(matrix: List[List[int]]) -> bool:
        # Get the size of the matrix (assuming it's a square matrix)
        n = len(matrix)

        # Iterate through each row and corresponding column
        for row, col in zip(matrix, zip(*matrix)):
            # Check if the row has n unique elements
            if len(set(row)) != n:
                return False
            # Check if the column has n unique elements
            if len(set(col)) != n:
                return False

        # If all rows and columns have n unique elements, return True
        return True


print(Solution.checkValid(matrix=[[1, 1, 1], [1, 2, 3], [1, 2, 3]]))
