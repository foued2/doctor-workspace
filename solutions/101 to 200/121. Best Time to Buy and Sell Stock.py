from typing import List


class Solution:
    @staticmethod
    def maxProfit(prices: List[int]) -> int:
        if not prices or len(prices) == 1:
            return 0

        # Initialize variables
        n = len(prices)
        dp = [0] * n  # dp[i] represents the maximum profit at day i
        min_price = prices[0]

        # Update dp array
        for i in range(1, n):
            # For each day `i`, `dp[i]` is updated to be the maximum of either the profit obtained on the
            # previous day (`dp[i-1]`) or the profit that can be obtained by selling the stock on the current day
            # (`prices[i] - min_price`).
            dp[i] = max(dp[i - 1], prices[i] - min_price)
            min_price = min(min_price, prices[i])

        return dp[-1]


# Example usage:
solution = Solution()
print(solution.maxProfit([7, 1, 5, 3, 6, 4]))

