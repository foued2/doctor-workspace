from typing import List


class Solution:
    @staticmethod
    def findTheArrayConcVal(nums: List[int]) -> int:
        # Get the initial length of the list
        n = len(nums)
        # Initialize the variable to store the concatenated value sum
        concat = 0

        # Continue looping while there are elements in the list
        while nums:
            if n > 1:
                # Concatenate the first and last elements as strings, then convert to integer
                concat += int(str(nums[0]) + str(nums[-1]))
                # Remove the first element
                nums.pop(0)
                # Remove the last element
                nums.pop()
                # Decrease the length counter by 2
                n -= 2
            elif n == 1:
                # If only one element is left, add it to the concatenated value sum
                concat += nums[0]
                # Remove the only remaining element
                nums.pop(0)
                # Decrease the length counter by 1
                n -= 1

        # Return the final concatenated value sum
        return concat


print(Solution.findTheArrayConcVal(
    nums=[72, 8, 96, 78, 39, 92, 69, 55, 9, 44, 26, 76, 40, 77, 16, 69, 40, 64, 12, 48, 66, 7, 59, 10, 33, 72, 97, 60,
          79, 68, 25, 63, 82, 88, 60, 37, 60, 44, 14, 62]))
