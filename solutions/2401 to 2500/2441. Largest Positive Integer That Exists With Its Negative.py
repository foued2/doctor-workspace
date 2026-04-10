from typing import List


class Solution:
    @staticmethod
    def findMaxK(nums: List[int]) -> int:
        """
        Two pointers
        """
        # Get the length of the input list
        n = len(nums)

        # Sort the list in ascending order
        nums.sort()

        # If the maximum element in the list is negative, return -1
        if nums[-1] < 0:
            return -1

        # Initialize two pointers, left and right, to the start and end of the list respectively
        left, right = 0, n - 1

        # Loop until the left pointer is less than the right pointer
        while left < right:
            # If the absolute value of the element at the left pointer is equal to the element at the right pointer
            if nums[left] == -nums[right]:
                # Return the element at the right pointer
                return nums[right]
            # If the absolute value of the element at the left pointer is less than the element at the right pointer
            elif nums[left] < -nums[right]:
                # Move the left pointer to the right
                left += 1
            # If the absolute value of the element at the left pointer is greater than the element at the right pointer
            else:
                # Move the right pointer to the left
                right -= 1

        # If no element is found that satisfies the condition, return -1
        return -1


print(Solution.findMaxK(nums=[-10, 8, 6, 7, -2, -3]))
