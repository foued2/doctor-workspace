from typing import List


class NumArray:
    def __init__(self, nums: List[int]):
        """
        Initializes a NumArray object with the given list of integers.
        Args:
        - nums: A list of integers representing the elements of the NumArray.
        """
        self.nums = nums
        self.length = len(nums)

        # Initialize a dynamic programming array to store cumulative sums
        self.dp = self._initialize_dp(nums)

    @staticmethod
    def _initialize_dp(nums: List[int]) -> List[int]:
        """
        Initializes the dynamic programming array to store cumulative sums.
        Args:
        - nums: A list of integers representing the elements of the NumArray.
        Returns:
        - The initialized dynamic programming array with cumulative sums.
        """
        dp = [0] * (len(nums) + 1)
        for i in range(1, len(nums) + 1):
            dp[i] = nums[i - 1] + dp[i - 1]
        return dp

    def sumRange(self, left: int, right: int) -> int:
        """
        Computes the sum of elements within the specified range [left, right].
        Args:
        - left: The left index of the range.
        - right: The right index of the range.
        Returns:
        - The sum of elements within the specified range [left, right].
        """
        # Compute the sum of elements within the specified range
        # by subtracting the cumulative sum at 'left - 1' (if 'left > 0')
        # from the cumulative sum at 'right'
        return self.dp[right + 1] - self.dp[left]


# Test the solution
lst = [-2, 0, 3, -5, 2, -1]
i, j = 0, 2
obj = NumArray(lst)
param_1 = obj.sumRange(i, j)  # Output: 1
print(param_1)

i, j = 2, 5
param_2 = obj.sumRange(i, j)  # Output: -1
print(param_2)

i, j = 0, 5
param_3 = obj.sumRange(i, j)  # Output: -3
print(param_3)


