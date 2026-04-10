from typing import List


class Solution:
    @staticmethod
    def rotate(nums: List[int], k: int):
        """
        Do not return anything, modify nums in-place instead.
        """
        # Calculate the effective rotation steps
        k %= len(nums)

        # Define the reverse function
        def reverse(nums, start, end):
            while start < end:
                nums[start], nums[end] = nums[end], nums[start]
                start += 1
                end -= 1

        # Reverse the entire array
        reverse(nums, 0, len(nums) - 1)
        # Reverse the first k elements
        reverse(nums, 0, k - 1)
        # Reverse the remaining elements
        reverse(nums, k, len(nums) - 1)
        return nums


print(Solution.rotate(nums=[1, 2, 3, 4, 5, 6, 7], k=3))
