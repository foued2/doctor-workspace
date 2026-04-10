from typing import List


class Solution:
    @staticmethod
    def hasTrailingZeros(nums: List[int]) -> bool:
        """
        Bit manipulation
        """
        # Counter-to-track numbers with trailing zeros
        trailing_zeros_count = 0

        # Iterate through each number in the list
        for number in nums:
            # Check if the number has a trailing zero (is even)
            if number & 1 == 0:
                trailing_zeros_count += 1
            # If at least two numbers have trailing zeros, return True
            if trailing_zeros_count == 2:
                return True

        # Return False if fewer than two numbers have trailing zeros
        return False


# Example usage
nums = [1, 2, 3, 4, 5]
solution = Solution()
print(solution.hasTrailingZeros(nums))  # Output: True
