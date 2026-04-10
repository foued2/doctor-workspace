from collections import Counter
from typing import List


class Solution:
    @staticmethod
    def unequalTriplets(nums: List[int]) -> int:
        # Count the frequency of each number in the input list
        frequency = Counter(nums)
        # Initialize the result count for unique triplets
        result = 0

        # Initialize the left pointer (sum of frequencies processed so far)
        left_sum = 0
        # Initialize the right pointer (total number of elements)
        right_sum = len(nums)

        # Iterate through each unique number and its frequency in the frequency dictionary
        for _, count in frequency.items():
            # Adjust the right pointer by subtracting the current frequency
            right_sum -= count
            # Calculate the number of unique triplets using the left, current, and right frequencies
            result += left_sum * count * right_sum
            # Update the left pointer by adding the current frequency
            left_sum += count

        # Return the total number of unique triplets
        return result


# Example usage
print(Solution().unequalTriplets(nums=[1, 3, 1, 2, 4]))  # Output: 7

