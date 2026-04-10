from typing import List


class Solution:
    @staticmethod
    def findMiddleIndex(nums: List[int]) -> int:
        # Initialize the answer to -1, meaning no middle index found yet
        ans = -1
        # Add padding with zero at the start and end of the list
        nums = [0] + nums + [0]
        # Length of the padded list
        n = len(nums)
        # Calculate the total sum of the padded list
        total = sum(nums)
        # Initialize the left sum to 0
        left_sum = 0

        # Iterate through the padded list from the first actual element to the last actual element
        for i in range(1, n - 1):
            # Update the left sum to include the previous element
            left_sum += nums[i - 1]
            # Calculate the right sum by subtracting the current left sum and the current element from the total sum
            right_sum = total - left_sum - nums[i]

            # Check if the left sum is equal to the right sum
            if left_sum == right_sum:
                # If they are equal, update the answer to the current index minus 1 (adjust for padding)
                ans = i - 1
                # Exit the loop as we found the middle index
                break

        # Return the answer, either the found index or -1 if no such index exists
        return ans


# Test case
nums = [-1000, 1000]

# Create an instance of Solution and test the method
solution = Solution()
output = solution.findMiddleIndex(nums)
print(output)  # Expected: -1

# Example usage:
nums = [2, 3, -1, 8, 4]
print(Solution.findMiddleIndex(nums))  # Output: 3

print(Solution.findMiddleIndex(nums=[1, -1, 4]))
