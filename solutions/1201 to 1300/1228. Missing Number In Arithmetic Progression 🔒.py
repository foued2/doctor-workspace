from typing import List


class Solution:
    @staticmethod
    def missingNumber(arr: List[int]) -> int:
        # Calculate the expected sum of the arithmetic progression if no number were missing.
        # The formula for the sum of the first n terms of an arithmetic progression is:
        # sum = n * (first_term + last_term) / 2
        # Here, n is len(arr) + 1 because one term is missing in the array.
        n = len(arr) + 1
        expected_sum = (arr[0] + arr[-1]) * n // 2

        # Calculate the actual sum of the array
        actual_sum = sum(arr)

        # The missing number is the difference between the expected sum and the actual sum
        missing_number = expected_sum - actual_sum

        return missing_number


print(Solution.missingNumber(arr=[15, 13, 12]))
