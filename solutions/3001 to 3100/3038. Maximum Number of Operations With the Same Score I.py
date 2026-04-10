from typing import List


class Solution:
    @staticmethod
    def maxOperations(nums: List[int]) -> int:
        # Initialize a variable to count the number of operations
        count = 0

        # Get the length of the input list
        n = len(nums)

        # Initialize an index variable
        i = 0

        # Calculate the score by adding the first two elements of the list
        score = nums[0] + nums[1]

        # Iterate through the list by pairs
        while i + 1 < n:
            # Get the current pair of numbers
            num1, num2 = nums[i], nums[i + 1]

            # If the sum of the current pair is not equal to the calculated score, return the count
            if num1 + num2 != score:
                return count

            # Increment the count as the current pair contributes to an operation
            count += 1

            # Move to the next pair by incrementing the index by 2
            i += 2

        # Return the count of operations
        return count


print(Solution.maxOperations(nums=[3, 2, 1, 4, 5]))
