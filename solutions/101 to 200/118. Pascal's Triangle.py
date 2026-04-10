from typing import List  # Importing List from typing module


class Solution:
    @staticmethod
    def generate(numRows: int) -> List[List[int]]:
        # Create a 2D list to store Pascal's Triangle
        dp = [[1] * (i + 1) for i in range(numRows)]
        # ((i-1) // 2) * i : pair
        # Iterate through each row
        for i in range(numRows):
            # Iterate through each element in the row
            for j in range(1, i):
                # Calculate each element based on the sum of the elements above and to the left
                dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]
            # for row in dp:
            print(i, dp[i])
        # Return the generated Pascal's Triangle
        return dp

    print(generate(10))
