from typing import List


class Solution:
    @staticmethod
    def removeDuplicates(nums: List[int]) -> int:
        # Edge case: if the array has 0 or 1 elements, duplicates can't exist.
        if len(nums) <= 2:
            return len(nums)

        # Initialize pointers
        write_index = 2  # Position to write the next non-duplicate element

        # Iterate through the array starting from the third element
        for i in range(2, len(nums)):
            # If the current element is different from the element at the write index, or
            # it's different from the previous two elements, we keep it in the array.
            if nums[i] != nums[write_index - 2]:
                nums[write_index] = nums[i]
                write_index += 1

        return write_index

    # Test the function
    nums = [0, 0, 1, 1, 1, 1, 2, 3, 3]
    new_length = removeDuplicates(nums)
    print("New Length:", new_length)
    print("Modified Array:", nums[:new_length])
