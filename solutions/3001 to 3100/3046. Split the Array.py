from typing import List


class Solution:
    @staticmethod
    def isPossibleToSplit(nums: List[int]) -> bool:
        # Initialize a dictionary to keep track of the count of each number
        table = {}

        # Iterate over each number in the input list
        for num in nums:
            # Increment the count of the current number in the table
            table[num] = table.get(num, 0) + 1

            # If any number appears three times, return False
            if table[num] == 3:
                return False

        # If no number appears three times, return True
        return True


# Example usage:
nums = [1, 2, 2, 3, 3, 4]
solution = Solution()
print(solution.isPossibleToSplit(nums))  # Output should be True

nums = [1, 2, 2, 3, 3, 3]
print(solution.isPossibleToSplit(nums))  # Output should be False
