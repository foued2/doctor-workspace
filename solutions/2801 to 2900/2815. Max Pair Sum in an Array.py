from collections import defaultdict  # Importing defaultdict to handle dictionary with default list values
from typing import List  # Importing List from typing module for type hinting


class Solution:
    @staticmethod  # Indicating that maxSum is a static method and doesn't depend on instance of the class
    def maxSum(nums: List[int]) -> int:
        ans = -1  # Initialize the answer to -1 (to handle the case where no valid pairs are found)

        # Sort the numbers in descending order
        nums = sorted(nums, reverse=True)

        # Convert each number to a list of its digits (as strings)
        copy = [list(str(num)) for num in nums]

        # Create a defaultdict to store lists of numbers keyed by their maximum digit
        table = defaultdict(list)

        # Populate the dictionary
        for i in range(len(copy)):
            curr = max(copy[i])  # Find the maximum digit in the current number
            table[curr].append(nums[i])  # Append the original number to the list corresponding to the max digit

        # Iterate through the dictionary to find the maximum sum of pairs
        for key, value in table.items():
            if len(value) >= 2:  # Only consider lists with at least two elements
                curr = sum(value[:2])  # Sum the two largest numbers (since the list is sorted in descending order)
                ans = max(ans, curr)  # Update the answer if the current sum is greater

        return ans  # Return the maximum sum found


print(Solution.maxSum(nums=[87, 6, 17, 32, 14, 42, 46, 65, 43, 9]))
