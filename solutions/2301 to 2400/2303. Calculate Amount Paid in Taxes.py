from typing import List


class Solution:
    @staticmethod
    def calculateTax(brackets: List[List[int]], income: int) -> float:
        # Initialize the total tax to 0
        ans = 0.0

        # Initialize the previous upper limit to 0
        prev = 0

        # Iterate over each bracket
        for bracket in brackets:
            upper, percent = bracket  # Extract the upper limit and the tax percentage for the current bracket

            if income > upper:
                # Calculate the income within the current bracket
                tax_money = upper - prev
            else:
                # If the income is within the current bracket, calculate the remaining income
                tax_money = income - prev

            # Add the tax for the current bracket to the total tax
            ans += tax_money * (percent / 100)

            # Update the previous upper limit to the current upper limit
            prev = upper

            # If income is less than or equal to the current upper limit, break the loop
            if income <= upper:
                break

        # Return the total calculated tax
        return ans


# Example usage:
brackets = [[10000, 10], [20000, 20], [30000, 30]]
income = 25000
print(Solution.calculateTax(brackets, income))  # Expected output: 4000.0

print(Solution.calculateTax(brackets=[[3, 50], [7, 10], [12, 25]], income=10))
