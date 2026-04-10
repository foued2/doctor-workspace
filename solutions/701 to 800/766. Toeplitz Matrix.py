from typing import List


class Solution:
    @staticmethod
    def isToeplitzMatrix(iterator) -> bool:
        """
        Matrix, Partial row loading (large input)
        """
        # Initialize the previous row to None
        prev_row = None

        # Loop through the matrix row by row
        for row in iterator:
            if prev_row is not None:
                # Compare each element with the element diagonally above it
                for j in range(1, len(row)):
                    if row[j] != prev_row[j - 1]:
                        return False
            # Update the previous row to be the current row
            prev_row = row

        # If all elements match the condition, return True
        return True


# Example usage with an iterator that simulates reading from a large matrix
def matrix_generator(matrix: List[List[int]]):
    for row in matrix:
        yield row


matrix1 = [
    [1, 2, 3, 4],
    [5, 1, 2, 3],
    [9, 5, 1, 2]
]
print(Solution.isToeplitzMatrix(matrix_generator(matrix1)))  # Expected output: True

matrix2 = [
    [1, 2],
    [2, 2]
]
print(Solution.isToeplitzMatrix(matrix_generator(matrix2)))  # Expected output: False
