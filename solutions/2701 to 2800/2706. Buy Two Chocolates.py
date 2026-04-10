from typing import List


class Solution:
    @staticmethod
    def buyChoco(prices: List[int], money: int) -> int:
        # Sort the list of prices in ascending order
        prices = sorted(prices)

        # Check if the sum of the two cheapest chocolates is within the budget
        if prices[0] + prices[1] <= money:
            # If yes, return the remaining money after buying the two cheapest chocolates
            return money - prices[0] - prices[1]

        # If no, return the original amount of money as chocolates cannot be bought within the budget
        return money


print(Solution.buyChoco(prices=[3, 2, 3], money=3))
