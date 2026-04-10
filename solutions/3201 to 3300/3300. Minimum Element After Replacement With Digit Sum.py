from typing import List


class Solution:
    @staticmethod
    def digit_sum(n: int) -> int:
        total = 0
        while n:
            total += n % 10
            n //= 10
        return total

    @staticmethod
    def find_min_digit_sum(nums: List[int]) -> int:
        min_sum = float('inf')
        # Iterate through each number in the list.
        for num in nums:
            # Calculate the digit sum of the current number.
            curr_sum = Solution.digit_sum(num)
            # Update the minimum digit sum.
            min_sum = min(min_sum, curr_sum)
        return min_sum


if __name__ == '__main__':
    # Sample usage
    print(Solution().find_min_digit_sum(nums=[10, 12, 13, 14]))
