from typing import List


class Solution:
    @staticmethod
    def change(amount: int, coins: List[int]) -> int:
        """
        Dynamic Programming
        """
        # Create a table to store the number of combinations for each amount from 0 to amount
        dp = [0] * (amount + 1)
        dp[0] = 1  # Base case: there is one way to make amount 0 (use no coins)

        # Iterate through each coin denomination
        for coin in coins:
            # Update the dp table for each amount from coin to amount
            for i in range(coin, amount + 1):
                dp[i] += dp[i - coin]  # Add the number of combinations using the current coin

        return dp[amount]  # Return the number of combinations to make the target amount


if __name__ == '__main__':
    print(Solution.change(amount=5, coins=[1, 2, 5]))
    print(Solution.change(amount=3, coins=[2]))
    print(Solution.change(amount=10, coins=[10]))

