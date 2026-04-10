from typing import List
from collections import Counter


class Solution:
    @staticmethod
    def findLonely(nums: List[int]) -> List[int]:
        # Initialize an empty list to store the lonely numbers
        res = []

        # Create a Counter object to count the occurrences of each number in the list
        table = Counter(nums)

        # Iterate over each key-value pair in the Counter object
        for key, value in table.items():
            # Check if the current number appears exactly once
            if value == 1:
                # Check if neither (key - 1) nor (key + 1) are in the Counter object
                if (key - 1) not in table and (key + 1) not in table:
                    # If both conditions are satisfied, add the number to the result list
                    res.append(key)

        # Return the list of lonely numbers
        return res


# Example usage:
nums = [1, 3, 2, 2, 5, 7]
print(Solution.findLonely(nums))  # Output should be [1, 5, 7]

print(Solution.findLonely(nums=[10, 6, 5, 8]))
