from typing import List


class Solution:
    @staticmethod
    def matrixSum(nums: List[List[int]]) -> int:
        # Initialize the answer accumulator to 0
        ans = 0
        # Determine the number of rows
        m = len(nums)

        # Continue as long as there are non-empty rows
        while any(nums):
            # Initialize the maximum value of this iteration
            max_row = 0
            # Iterate over each row
            for i in range(m):
                # If the row is not empty
                if nums[i]:
                    # Find the maximum value in the current row
                    curr_pop = max(nums[i])
                    # Remove the maximum value from the current row
                    nums[i].remove(curr_pop)
                    # Update the maximum value for this iteration
                    max_row = max(max_row, curr_pop)
            # Add the maximum value of this iteration to the answer
            ans += max_row

        # Return the accumulated answer
        return ans
