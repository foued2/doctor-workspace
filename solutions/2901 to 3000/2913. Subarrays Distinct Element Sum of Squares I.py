from typing import List


class Solution:
    @staticmethod
    def sumCounts(nums: List[int]) -> int:
        # Initialize the variable to store the final answer
        ans = 0

        # Iterate through each starting index of the subarrays
        for i in range(len(nums)):
            # Initialize a set to keep track of unique elements in the current subarray
            s = set()

            # Iterate through the subarray starting at index i
            for j in range(i, len(nums)):
                # Add the current element to the set
                s.add(nums[j])

                # Add the square of the size of the set to the answer
                # This counts the sum of squares of the number of unique elements
                ans += len(s) ** 2

        # Return the accumulated answer
        return ans


# Example usage:
nums = [1, 2, 3]
solution = Solution()
print(solution.sumCounts(nums))  # Output: 20
