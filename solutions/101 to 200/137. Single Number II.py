from typing import List


class Solution:
    @staticmethod
    def singleNumber(nums: List[int]) -> int:
        """
        Bit manipulation
        """
        ones, twos = 0, 0

        for num in nums:
            # Update `twos` with bits that are set in both `ones` and the current number `num`
            twos |= ones & num
            # Update `ones` by XORing it with `num`
            ones ^= num
            # Calculate the bits that are set in both `ones` and `twos`
            threes = ones & twos
            # Remove bits from `ones` that have appeared three times
            ones &= ~threes
            # Remove bits from `twos` that have appeared three times
            twos &= ~threes

        # Return the single number that appears exactly once
        return ones


# Example usage
if __name__ == '__main__':
    print(Solution.singleNumber([2, 2, 3, 2]))  # Output should be 3, as 3 appears only once
    print(Solution.singleNumber([0, 1, 0, 1, 0, 1, 99]))  # Output should be 99, as 99 appears only once
