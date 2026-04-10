from typing import List


class Solution:
    @staticmethod
    def sumOfSquares(nums: List[int]) -> int:
        # Get the length of the list
        n = len(nums)

        # Initialize the result variable
        res = 0

        # Iterate through the indices of the list
        for i in range(n):
            # Check if the length of the list is divisible by (i + 1)
            if n % (i + 1) == 0:
                # If it is, add the square of the element at index i to the result
                res += nums[i] ** 2

        # Return the sum of squares
        return res


if __name__ == '__main__':
    print(Solution.sumOfSquares(nums=[2, 7, 1, 19, 18, 3]))
