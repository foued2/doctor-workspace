from typing import List


class Solution:
    @staticmethod
    def distinctDifferenceArray(nums: List[int]) -> List[int]:
        # Get the length of the input list
        n = len(nums)

        # Initialize an empty list to store the result
        result = []

        # Loop through each index of the input list
        for i in range(n):
            # Create a set from the left part of the list (including the current index)
            left_part = set(nums[:i + 1])

            # Create a set from the right part of the list (excluding the current index)
            right_part = set(nums[i + 1:])

            # Calculate the difference in the number of distinct elements
            distinct_difference = len(left_part) - len(right_part)

            # Append the difference to the result list
            result.append(distinct_difference)

        # Return the final result list
        return result


# Example usage:
sol = Solution()
print(sol.distinctDifferenceArray([1, 2, 3, 2, 1, 4]))

print(Solution.distinctDifferenceArray(nums=[3, 2, 3, 4, 2]))
