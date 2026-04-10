from typing import List


class Solution:
    @staticmethod
    def zeroFilledSubarray(nums: List[int]) -> int:
        # Initialize the answer to zero.
        ans = 0
        # Get the length of the input list.
        n = len(nums)
        # Initialize the index for traversing the list.
        i = 0

        # Loop through the list until the end is reached.
        while i < n:
            # Initialize the streak length of consecutive zeros to zero.
            streak = 0

            # Check if the current element is zero.
            if nums[i] == 0:
                # Initialize the streak length to 1 since we found a zero.
                streak = 1
                # Check for consecutive zeros.
                while i + 1 < n and nums[i] == nums[i + 1] == 0:
                    # Increase the streak length.
                    streak += 1
                    # Move to the next element in the list.
                    i += 1

            # Calculate the number of subarrays that can be formed from the current streak of zeros.
            # This is the sum of the first 'streak' natural numbers.
            ans += (streak * (streak + 1)) // 2
            # Move to the next element in the list.
            i += 1

        # Return the total number of zero-filled subarrays.
        return ans


print(Solution.zeroFilledSubarray(nums=[0, 0, 0, 2, 0, 0]))
