from typing import List


class Solution:
    @staticmethod
    def sortColors(nums: List[int]) -> List[int]:
        """
        Do not return anything, modify nums in-place instead.
        """
        # Initialize pointers for the leftmost and rightmost elements
        left, right = 0, len(nums) - 1
        # Initialize a pointer for iterating through the array
        i = 0

        # Iterate through the array until the iterator crosses the right pointer
        while i <= right:
            # If the current element is 0, swap it with the leftmost element
            if nums[i] == 0:
                nums[i], nums[left] = nums[left], nums[i]
                # Move the left pointer to the right
                left += 1
                # Move the iterator to the next element
                i += 1
            # If the current element is 2, swap it with the rightmost element
            elif nums[i] == 2:
                nums[i], nums[right] = nums[right], nums[i]
                # Move the right pointer to the left
                right -= 1
            else:
                # If the current element is 1, leave it in place and move to the next element
                i += 1

        # Return the sorted array
        return nums

    # Test the function
    print(sortColors(nums=[2, 0, 2, 1, 1, 0]))