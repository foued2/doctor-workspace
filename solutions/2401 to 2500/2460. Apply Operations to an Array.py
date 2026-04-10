from typing import List


class Solution:
    @staticmethod
    def applyOperations(nums: List[int]) -> List[int]:
        # Get the length of the input list
        n = len(nums)

        # This pointer will track the position to place the non-zero elements
        write_index = 0

        # First pass: combine the same elements and set the second of the pair to zero
        for i in range(n - 1):
            # Check if the current element is equal to the next element and not zero
            if nums[i] == nums[i + 1] and nums[i] != 0:
                # If they are equal, double the current element and set the next element to 0
                nums[i] *= 2
                nums[i + 1] = 0

        # Second pass: move non-zero elements to the front and count zeros
        for i in range(n):
            # If the current element is non-zero
            if nums[i] != 0:
                # Move it to the position indicated by write_index
                nums[write_index] = nums[i]
                # Increment the write_index
                write_index += 1

        # Fill the remaining part of the list with zeros
        for i in range(write_index, n):
            # Set the element at index i to 0
            nums[i] = 0

        # Return the modified list
        return nums


print(Solution.applyOperations(nums=[847, 847, 0, 0, 0, 399, 416, 416, 879, 879, 206, 206, 206, 272]))
