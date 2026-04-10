from typing import List


class Solution:
    @staticmethod
    def minimumTotal(triangle: List[List[int]]) -> int:
        # Initialize the dp array with the values of the bottom row of the triangle
        dp = triangle[-1].copy()

        # Iterate through the rows of the triangle from bottom to top
        for i in range(len(triangle) - 2, -1, -1):
            # Iterate through each element in the current row
            for j in range(len(triangle[i])):
                # Update dp values by considering the minimum path sum from the row below
                if j < len(dp) - 1:
                    dp[j] = min(triangle[i][j] + dp[j], triangle[i][j] + dp[j + 1])
                else:
                    dp[j] = triangle[i][j]

        # Return the minimum path sum, which is stored at the top of the dp array
        return dp[0]


# Example usage:
solution = Solution()
result = solution.minimumTotal(triangle=[[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]])
print(result)
