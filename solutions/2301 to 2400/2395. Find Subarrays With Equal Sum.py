from typing import List


class Solution:
    @staticmethod
    def findSubarrays(nums: List[int]) -> bool:
        n = len(nums)  # Get the length of the input list.
        table = {}  # Initialize an empty dictionary to store sums of subarrays.

        # Iterate through the list starting from the second element.
        for i in range(1, n):
            # Calculate the sum of the current element and the previous element.
            current_sum = nums[i] + nums[i - 1]

            # Check if the current sum is already in the dictionary.
            if current_sum in table:
                # If the sum is found, it means we have encountered another subarray with the same sum.
                return True
            else:
                # If the sum is not found, add it to the dictionary with the indices of the elements.
                table[current_sum] = [i, i - 1]

        # If no matching subarrays are found, return False.
        return False


print(Solution.findSubarrays(nums=[1, 2, 3, 4, 5]))
