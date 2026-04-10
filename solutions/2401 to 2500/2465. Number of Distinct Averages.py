from typing import List


class Solution:
    @staticmethod
    def distinctAverages(nums: List[int]) -> int:
        # Sort the list to easily find pairs
        nums = sorted(nums)
        # Initialize a set to store distinct averages
        res = set()

        # Use two pointers to iterate from both ends of the list
        left, right = 0, len(nums) - 1

        while left < right:
            # Calculate the average of the current pair
            average = (nums[left] + nums[right]) / 2
            # Add the average to the set
            res.add(average)
            # Move the left pointer to the right
            left += 1
            # Move the right pointer to the left
            right -= 1

        # Return the number of distinct averages
        return len(res)


print(Solution.distinctAverages(nums=[9, 5, 7, 8, 7, 9, 8, 2, 0, 7]))
