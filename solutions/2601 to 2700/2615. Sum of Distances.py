from typing import List
from collections import defaultdict


class Solution:
    @staticmethod
    def distance(nums: List[int]) -> List[int]:
        """
        Prefix and Suffix Sums
        """
        n = len(nums)
        res = [0] * n

        # Dictionary to store the sum of indices of occurrences for a number
        index_sum = defaultdict(int)
        # Dictionary to store the count of occurrences for a number
        count = defaultdict(int)

        # Compute prefix sums and counts for all elements
        for i, num in enumerate(nums):
            res[i] += count[num] * i - index_sum[num]
            index_sum[num] += i
            count[num] += 1

        # Reset dictionaries to compute suffix sums and counts
        index_sum.clear()
        count.clear()

        # Compute suffix sums and counts for all elements in reverse order
        for i in range(n - 1, -1, -1):
            num = nums[i]
            res[i] += index_sum[num] - count[num] * i
            index_sum[num] += i
            count[num] += 1

        return res


if __name__ == "__main__":
    print(Solution().distance(nums=[1, 3, 1, 1, 2]))
