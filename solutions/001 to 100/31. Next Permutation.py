from typing import List


class Solution:
    @staticmethod
    def nextPermutation(nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        i = len(nums) - 2

        # Find the first pair of two successive numbers nums[i] and nums[i+1]
        # from the right, such that nums[i] < nums[i+1]
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1

        if i >= 0:
            # Find the smallest element to the right of nums[i] but larger than nums[i]
            j = len(nums) - 1
            while j >= 0 and nums[j] <= nums[i]:
                j -= 1

            # Swap nums[i] and nums[j]
            nums[i], nums[j] = nums[j], nums[i]
        print(nums)
        # Reverse the sub-array to the right of nums[i]
        left, right = i + 1, len(nums) - 1
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
        return nums

    print(nextPermutation([1, 1, 3, 4, 5, 5, 3]))
