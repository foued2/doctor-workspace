from typing import List


class Solution:
    @staticmethod
    def sortArrayByParity(nums: List[int]) -> List[int]:
        # Initialize a variable to keep track of the index where the next even number should be placed
        even = 0

        # Iterate through the array using a for loop
        for i in range(len(nums)):
            # Check if the current number at index i is even
            if nums[i] % 2 == 0:
                # If it's even, swap it with the number at index 'even'
                nums[even], nums[i] = nums[i], nums[even]
                # Increment 'even' to move to the next position where an even number should be placed
                even += 1

        # Return the modified array where even numbers are moved to the beginning
        return nums


# Example usage:
nums = [3, 1, 2, 4, 7, 8, 6, 5]
sorted_nums = Solution.sortArrayByParity(nums)
print(sorted_nums)  # Output: [6, 8, 2, 4, 7, 1, 3, 5]
