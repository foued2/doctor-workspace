from typing import List


class Solution:
    @staticmethod
    def rotate(matrix: List[List[int]]) -> List[List[int]]:
        """
        Rotate the given matrix by 90 degrees in place.

        Args:
        - matrix: The matrix to rotate.

        Returns:
        - The rotated matrix.
        """
        n = len(matrix)
        # We iterate over half of the rows because we are swapping elements in pairs.
        for i in range(n // 2):
            # We iterate over the columns until the middle column.
            for j in range(i, n - i - 1):
                # Perform a 4-way swap to rotate the elements.
                # Save the top-left element.
                temp = matrix[i][j]
                # Move the bottom-left element to the top-left.
                matrix[i][j] = matrix[n - j - 1][i]
                # Move the bottom-right element to the bottom-left.
                matrix[n - j - 1][i] = matrix[n - i - 1][n - j - 1]
                # Move the top-right element to the bottom-right.
                matrix[n - i - 1][n - j - 1] = matrix[j][n - i - 1]
                # Move the top-left (saved) element to the top-right.
                matrix[j][n - i - 1] = temp
        return matrix


# Test the rotation function
print(Solution.rotate(matrix=[[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
