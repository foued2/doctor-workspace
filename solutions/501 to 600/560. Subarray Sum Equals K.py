from typing import List
from collections import defaultdict


class Solution:
    @staticmethod
    def subarraySum(nums: List[int], k: int) -> int:
        # Initialize a dictionary to store cumulative sums and their frequencies.
        sum_freq = defaultdict(int)
        cumulative_sum = 0
        count = 0

        # Initialize the cumulative sum of the empty subarray.
        sum_freq[0] = 1

        # Iterate through the array, calculate cumulative sums,
        # and check if (cumulative_sum - k) exists in sum_freq.
        for num in nums:
            cumulative_sum += num
            count += sum_freq[cumulative_sum - k]
            sum_freq[cumulative_sum] += 1

        return count


# Test the function
if __name__ == "__main__":
    print(Solution.subarraySum(nums=[1, 2, 3], k=3))  # Output: 2
