from typing import List


class Solution:
    @staticmethod
    def moveZeroes(nums: List[int]) -> None:
        """
        Modify nums in-place by moving all zeroes to the end.
        """
        # Initialize a pointer for the leftmost non-zero element
        left = 0

        # Iterate through the array
        for i in range(len(nums)):
            # If the current element is non-zero
            if nums[i] != 0:
                # Swap the current element with the leftmost non-zero element
                nums[left], nums[i] = nums[i], nums[left]
                # Move the left pointer to the right
                left += 1


# Test the function
if __name__ == '__main__':
    nums1 = [0, 1, 0, 3, 12]
    Solution.moveZeroes(nums1)
    print(nums1)  # Output: [1, 3, 12, 0, 0]

    nums2 = [2, 1]
    Solution.moveZeroes(nums2)
    print(nums2)  # Output: [2, 1]
