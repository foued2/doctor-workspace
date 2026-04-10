import collections
from typing import List


class Solution:
    @staticmethod
    def subarraysWithKDistinct(nums: List[int], k: int) -> int:
        def subarraysWithAtMostKDistinct(distinct_limit: int) -> int:
            # Initialize variables
            total_subarrays = 0
            num_count = collections.Counter()
            left_pointer = 0

            # Iterate through the array with a sliding window
            for right_pointer, num in enumerate(nums):
                # Increment count of current number
                num_count[num] += 1

                # If a new distinct number is encountered, decrement the distinct limit
                if num_count[num] == 1:
                    distinct_limit -= 1

                    # Shrink the window until distinct count is less than or equal to distinct_limit
                while distinct_limit < 0:
                    # Decrement count of the number at the left pointer
                    num_count[nums[left_pointer]] -= 1
                    # If the count becomes zero, increment the distinct limit
                    if num_count[nums[left_pointer]] == 0:
                        distinct_limit += 1
                        # Move the left pointer forward
                    left_pointer += 1

                # Calculate the number of subarrays with at most distinct_limit distinct integers
                total_subarrays += right_pointer - left_pointer + 1

            return total_subarrays

        # Calculate the number of subarrays with exactly k distinct integers
        return subarraysWithAtMostKDistinct(k) - subarraysWithAtMostKDistinct(k - 1)


if __name__ == '__main__':
    print(Solution.subarraysWithKDistinct(nums=[1, 2, 1, 2, 3], k=2))
    print(Solution.subarraysWithKDistinct(nums=[1, 2, 1, 3, 4], k=3))
    print(Solution.subarraysWithKDistinct(nums=[1, 2], k=1))
