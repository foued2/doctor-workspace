from typing import List


class Solution:
    @staticmethod
    def waysToSplitArray(nums: List[int]) -> int:
        # Initialize the answer to 0, this will hold the number of valid splits
        ans = 0
        # Get the length of the nums array
        n = len(nums)
        # Initialize the left sum to 0
        left = 0
        # Calculate the initial right sum as the sum of all elements in the array
        right = sum(nums)

        # Loop through the array up to the second last element
        for i in range(n - 1):
            # Add the current element to the left sum
            left += nums[i]
            # Subtract the current element from the right sum
            right -= nums[i]
            # If the left sum is greater than or equal to the right sum
            if left >= right:
                # Increment the answer count as it's a valid split
                ans += 1

        # Return the total number of valid splits
        return ans


print(Solution.waysToSplitArray(nums=[10, 4, -8, 7]))
