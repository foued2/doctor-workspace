from typing import List


class Solution:
    @staticmethod
    def minimumDifference(nums: List[int], k: int) -> int:
        # If k is 1, the difference is 0 because the subset will have only one element
        if k == 1:
            return 0

        # Sort the array
        nums.sort()

        # Initialize the answer with a large value
        ans = float('inf')

        # Iterate through the sorted array using a sliding window of size k
        for i in range(len(nums) - k + 1):
            # Compute the difference between the maximum and minimum in the current window
            diff = nums[i + k - 1] - nums[i]
            # Update the answer with the minimum difference found
            ans = min(ans, diff)

        # Return the minimum difference
        return ans


# Example usage
solution = Solution()
result = solution.minimumDifference([9, 4, 1, 7], 2)
print(result)  # Output: 2

print(Solution.minimumDifference(nums=[9, 4, 1, 7], k=3))

