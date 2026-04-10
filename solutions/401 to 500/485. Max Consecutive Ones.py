from typing import List


class Solution:
    @staticmethod
    def findMaxConsecutiveOnes(nums: List[int]) -> int:
        max_count = 0  # Initialize variable to store the maximum count of consecutive 1s
        count = 0  # Initialize count of current consecutive 1s

        # Iterate through each number in the binary array
        for num in nums:
            if num == 1:
                count += 1  # Increment the count if the current number is 1
                max_count = max(max_count, count)  # Update the max_count if the current count is greater
            else:
                count = 0  # Reset count to 0 if the current number is not 1

        return max_count  # Return the maximum count of consecutive 1s found


# Example usage
if __name__ == '__main__':
    print(Solution().findMaxConsecutiveOnes([1, 1, 0, 1, 1, 1]))  # Output: 3