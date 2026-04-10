from typing import List


class Solution:
    @staticmethod
    def coinChange(coins: List[int], amount: int) -> float:
        """
        Stack, Dynamic Programming
        """
        # Initialize an array to store the minimum number of coins required for each amount from 0 to amount
        dp = [float('inf')] * (amount + 1)

        # Base case: 0 coins are needed to make change for 0 amounts
        dp[0] = 0

        # Iterate over each coin
        for coin in coins:
            # Update dp array for amounts that can be made using the current coin
            for i in range(coin, amount + 1):
                # Update dp[i] with the minimum of current dp[i] and dp[i - coin] + 1
                dp[i] = min(dp[i], dp[i - coin] + 1)

        # If dp[amount] is still float('inf'), no combination of coins can make the amount
        if dp[amount] == float('inf'):
            return -1
        else:
            return dp[amount]


if __name__ == '__main__':
    # Test the coinChange function with the provided example
    print(Solution.coinChange(coins=[1, 2, 5], amount=11))
