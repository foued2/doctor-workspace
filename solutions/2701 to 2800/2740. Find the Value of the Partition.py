from typing import List


class Solution:
    @staticmethod
    def findValueOfPartition(nums: List[int]) -> int:
        # Initialize the answer to positive infinity, as we are looking for the minimum value
        ans = float('inf')

        # Get the length of the list
        n = len(nums)

        # Sort the list to bring similar values closer together
        nums = sorted(nums)

        # Iterate through the sorted list, stopping one element before the end
        for i in range(n - 1):
            # Calculate the difference between consecutive elements
            diff = nums[i + 1] - nums[i]

            # Update the answer with the minimum difference found so far
            ans = min(ans, diff)

        # Return the smallest difference found
        return ans


# Example usage:
nums = [1, 3, 6, 19, 20]
solution = Solution()
print(solution.findValueOfPartition(nums))  # Output should be 1 (the difference between 19 and 20)

print(Solution.findValueOfPartition(nums=[100, 1, 10]))
