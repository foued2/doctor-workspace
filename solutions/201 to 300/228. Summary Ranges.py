from typing import List


class Solution:
    @staticmethod
    def summaryRanges(nums: List[int]) -> List[str]:
        # Check if the list is empty
        if not nums:
            return []

        ranges = []  # Initialize an empty list to store ranges
        i = 0  # Initialize index for iterating through nums
        while i < len(nums):
            start = nums[i]  # Current start of the range
            # Find the end of the consecutive sequence
            while i + 1 < len(nums) and nums[i + 1] - nums[i] == 1:
                i += 1
            end = nums[i]  # Current end of the range
            # Construct the range string based on whether it's a single number or a range
            if start == end:
                ranges.append(str(start))  # Append single number to ranges
            else:
                ranges.append(str(start) + "->" + str(end))  # Append range to ranges
            i += 1  # Move to the next number in nums

        return ranges  # Return the list of ranges


# Test the function
print(Solution.summaryRanges([0, 1, 2, 4, 5, 7]))
