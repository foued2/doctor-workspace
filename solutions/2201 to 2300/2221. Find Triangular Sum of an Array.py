from typing import List


class Solution:
    @staticmethod
    def triangularSum(nums: List[int]) -> int:
        # Initialize a result to 0. This will store the final triangular sum.
        result = 0

        # Initialize ncr (combination value) to 1. This will store the binomial coefficient.
        ncr = 1

        # Calculate the length of the input list nums and subtract 1 to get the highest index.
        length = len(nums) - 1

        # Iterate through each element in the input list nums along with its index.
        for i, num in enumerate(nums):
            # Calculate the triangular sum modulo 10 and update the result.
            result = (result + num * ncr) % 10

            # Update the binomial coefficient for the next iteration using the formula:
            # nCr = nCr * (length - i) / (i + 1)
            ncr = (ncr * (length - i) // (i + 1))

        # Return the final triangular sum result.
        return result


# print(Solution.triangularSum(nums=[1, 2, 3, 4, 5]))
