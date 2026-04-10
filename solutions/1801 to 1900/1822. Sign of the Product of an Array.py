from typing import List


class Solution:
    @staticmethod
    def arraySign(nums: List[int]) -> int:
        # Define a helper function to determine the sign of a number
        def signFunc(x: int) -> int:
            if x > 0:
                return 1
            if x < 0:
                return -1
            else:
                return 0

        # Initialize the sign of the product
        product_sign = 1

        # Iterate over each number in the input list
        for num in nums:
            # If the number is zero, the product is zero
            if num == 0:
                return 0
            # If the number is negative, flip the sign of the product
            elif num < 0:
                product_sign *= -1

        # Return the sign of the product
        return product_sign


print(Solution.arraySign(nums=[-1, -2, -3, -4, 3, 2, 1]))
