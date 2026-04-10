# EASY // ARRAY // TWO POINTERS (First / Last)

from typing import List


class Solution:
    @staticmethod
    def removeElement(nums: List[int], val: int) -> int:
        # Return 0 if a list is empty
        if not nums:
            return 0

        # Initialize two pointers; right at the start of the list, left at the end
        right, left = 0, len(nums) - 1

        # Continue the loop while the right pointer is less than or equal to the left pointer
        while right <= left:
            # When the current element at the right pointer is equal to the given value,
            if nums[right] == val:
                # Replace the element at the right pointer with the element at the left pointer
                nums[right] = nums[left]
                # Decrement the left pointer
                left -= 1
            else:
                # If the current element at the right pointer is not equal to the given value,
                # increment the right pointer.
                right += 1
        # Return the modified list up to the right pointer and the new length.
        # It's up to the right pointer because the remaining elements would be excess ones that we swapped out.
        return nums[:right], right


# Testing the function
print(Solution.removeElement([0, 1, 2, 2, 3, 0, 4, 2], 2))
print(Solution.removeElement([3, 2, 2, 3], 3))
print(Solution.removeElement([1], 1))

# Input: nums = [0, 1, 2, 2, 3, 0, 4, 2], val = 2
# Output: 5, nums = [0, 1, 4, 0, 3, _, _, _]
#  3   2  2  3
#  0   1  2  3
# -1   0  1  2
