from typing import List


class Solution:
    @staticmethod
    def sumOfDigits(nums: List[int]) -> int:
        # Initialize the sum of digits of the minimum number
        sum_min_nums = 0

        # Find the minimum number in the list
        x = min(nums)

        # Calculate the sum of the digits of the minimum number
        while x:
            # Add the last digit of x to sum_min_nums
            sum_min_nums += x % 10

            # Remove the last digit from x
            x //= 10

        # If the sum of the digits is odd, return 0; otherwise, return 1
        return 0 if sum_min_nums % 2 != 0 else 1


# Example usage
solution = Solution()
print(solution.sumOfDigits([99, 25, 33, 47]))  # Output: 0 (since the minimum number is 25, and its digits sum to 7,
# which is odd)

print(Solution.sumOfDigits(nums=[34, 23, 1, 24, 75, 33, 54, 8]))
