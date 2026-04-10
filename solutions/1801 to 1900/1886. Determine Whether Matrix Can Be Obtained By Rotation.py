from typing import List


class Solution:
    @staticmethod
    def findRotation(mat: List[List[int]], target: List[List[int]]) -> bool:
        # Get the size of the matrix
        n = len(mat)

        # Iterate through 4 possible rotations (90 degrees, 180 degrees, 270 degrees, 360 degrees)
        for k in range(4):
            # Iterate through each layer of the matrix
            for i in range(n // 2):
                # Iterate over the columns until the middle column.
                for j in range(i, n - i - 1):
                    # Perform a 4-way swap to rotate the elements.

                    # Save the top-left element.
                    temp = mat[i][j]
                    # Move the bottom-left element to the top-left.
                    mat[i][j] = mat[n - j - 1][i]
                    # Move the bottom-right element to the bottom-left.
                    mat[n - j - 1][i] = mat[n - i - 1][n - j - 1]
                    # Move the top-right element to the bottom-right.
                    mat[n - i - 1][n - j - 1] = mat[j][n - i - 1]
                    # Move the top-left (saved) element to the top-right.
                    mat[j][n - i - 1] = temp

            # Check if the rotated matrix matches the target matrix
            if mat == target:
                return True

        # If no match is found after all rotations, return False
        return False


# Test the function
print(Solution.findRotation(mat=[[0, 1], [1, 1]], target=[[1, 0], [0, 1]]))

