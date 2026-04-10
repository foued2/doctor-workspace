from typing import List

class Solution:
    @staticmethod
    def maxProfit(prices: List[int]) -> int:
        # Initialize the buying price with the first price in the list
        curr_buy = prices[0]
        # Initialize the current profit to 0
        curr_profit = 0

        # Iterate through the prices starting from the second price
        for price in prices[1:]:
            # If the current buying price is greater than or equal to the current price,
            # it means there is no profit to make at this price.
            if curr_buy >= price:
                # Update the current buying price to the current price
                curr_buy = price
            # If the current buying price is less than the current price,
            # it means there is an opportunity to make a profit.
            else:
                # Calculate the profit by selling at the current price and subtracting the buying price
                # Add the profit to the current total profit
                curr_profit += price - curr_buy
                # Update the current buying price to the current price for potential future transactions
                curr_buy = price

        # Return the total profit obtained from all transactions
        return curr_profit


# Test the function
print(Solution.maxProfit(prices=[7, 6, 4, 3, 1]))
