from typing import List


class Solution:
    @staticmethod
    def minCostClimbingStairs(cost: List[int]) -> int:
        """
        Dynamic programming
        """
        # Get the length of the cost list
        n = len(cost)

        # Initialize a dynamic programming table to store minimum cost at each step
        dp = [0 for i in range(n + 1)]

        # Base cases for the first two steps
        dp[0] = 0
        dp[1] = cost[0]  # cost[0] represents the cost of reaching step 1

        # Loop through the steps, starting from the third step
        for i in range(2, n + 1):
            # At each step, calculate the minimum cost to reach it by considering the two previous steps
            dp[i] = cost[i - 1] + min(dp[i - 1], dp[i - 2])

        # The minimum cost to reach the top is the minimum between the cost of reaching the last two steps
        return min(dp[n], dp[n - 1])


if __name__ == '__main__':
    # Test cases
    print(Solution.minCostClimbingStairs(cost=[1, 100, 1, 1, 1, 100, 1, 1, 100, 1]))
    print(Solution.minCostClimbingStairs(cost=[10, 15, 20]))

