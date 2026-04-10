from typing import List


class Solution:
    @staticmethod
    def missingNumber(nums: List[int]) -> int:
        n = len(nums)

        # Sum of all numbers from 0 to n using arithmetic series formula
        total_sum = n * (n + 1) // 2
        # Sum of all numbers in the list
        actual_sum = sum(nums)

        # The missing number is the difference between the expected sum and the actual
        return total_sum - actual_sum
        # sum

    print(missingNumber(nums=[3, 0, 1]))
