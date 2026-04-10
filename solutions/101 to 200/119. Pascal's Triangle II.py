from typing import List


class Solution:
    @staticmethod
    def getRow(rowIndex: int) -> List[int]:
        # Create a 2D list to store Pascal's Triangle
        dp = [[1] * (i + 1) for i in range(rowIndex + 1)]

        # Iterate through each row
        for i in range(rowIndex + 1):
            # Iterate through each element in the row
            for j in range(1, i):
                # Calculate each element based on the sum of the elements above and to the left
                dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]

        # Return the last row as the result
        return dp[rowIndex]

    print(getRow(8))
