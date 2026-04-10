from typing import List


class Solution:
    @staticmethod
    def getMinDistance(nums: List[int], target: int, start: int) -> int:
        # Get the length of the nums list
        n = len(nums)

        # Initialize the answer to a very large number (infinity)
        ans = float('inf')

        # Iterate through each index in the nums list
        for i in range(n):
            # Check if the current element is equal to the target
            if nums[i] == target:
                # Calculate the absolute distance from the current index to the start index
                curr = abs(i - start)

                # Update the answer with the minimum distance found so far
                ans = min(ans, curr)

        # Return the minimum distance
        return ans


# Example usage
solution = Solution()
print(solution.getMinDistance(nums=[1, 2, 3, 4, 5], target=5, start=3))  # Output: 1
