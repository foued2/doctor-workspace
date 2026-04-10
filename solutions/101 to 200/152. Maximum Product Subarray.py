from typing import List


class Solution:
    @staticmethod
    def maxProduct(nums: List[int]) -> int:
        """
        Dynamic programming
        """
        n = len(nums)
        if n == 1:
            return nums[0]

        max_product = nums[0]

        dp = [0 for _ in range(n + 1)]
        dp[0] = nums[0]

        minus = 0  # Keeping count of negative numbers
        zero = 0  # Keeping count of zeroes

        for i in range(1, n):
            if nums[i] < 0:
                minus += 1
                if minus % 2 == 0:
                    dp[i] *= dp[i - 1]
                    # max_product = max(max_product, dp[i])
                else:
                    dp[i] = nums[i]
                max_product = max(max_product, dp[i])
            # elif nums[i] == 0:


if __name__ == '__main__':
    print(Solution.maxProduct(nums=[2, 3, -2, 4]))
    print(Solution.maxProduct([-1, 4, -4, 5, -2, -1, -1, -2, -3]))
