from math import floor


class Solution:
    @staticmethod
    def accountBalanceAfterPurchase(purchaseAmount: int) -> int:
        # Add a service fee of 5 to the purchase amount
        total_amount = purchaseAmount + 5
        # Calculate the total amount after dividing by 10 and rounding up to the nearest multiple of 10
        rounded_total = total_amount / 10
        # Round down the calculated total to the nearest multiple of 10
        rounded_down_total = floor(rounded_total)
        # Deduct the rounded-down total from the initial balance of 100 to get the remaining balance
        balance = 100 - (rounded_down_total * 10)
        # Return the remaining account balance after the purchase
        return balance


print(Solution.accountBalanceAfterPurchase(purchaseAmount=15))
