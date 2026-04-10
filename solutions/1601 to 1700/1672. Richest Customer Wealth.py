from typing import List


class Solution:
    @staticmethod
    def maximumWealth(accounts: List[List[int]]) -> int:
        # Initialize a variable to store the maximum wealth found
        # Iterate through each customer's account in the list of accounts
        # Calculate the sum of wealth for each customer and find the maximum
        ans = max(sum(row) for row in accounts)

        # Return the maximum wealth found
        return ans


print(Solution.maximumWealth(accounts=[[1, 5], [7, 3], [3, 5]]))
