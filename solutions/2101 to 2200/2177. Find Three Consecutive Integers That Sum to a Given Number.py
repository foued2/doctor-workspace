from typing import List


class Solution:
    @staticmethod
    def sumOfThree(num: int) -> List[int]:
        # Check if the given number can be expressed as the sum of three consecutive integers
        # Three consecutive integers are represented as: (x - 1), x, (x + 1)
        # Their sum is: (x - 1) + x + (x + 1) = 3x
        # Therefore, to find x, we need to check if num is divisible by 3

        # Check if num is divisible by 3
        if num % 3 == 0:
            # If divisible, find the middle integer
            third = num // 3
            # Return the three consecutive integers
            return [third - 1, third, third + 1]
        else:
            # If not divisible by 3, return an empty list as it's not possible
            return []


# Example usage:
# num = 33
# The function will find three consecutive integers whose sum is 33
print(Solution.sumOfThree(33))  # Output: [10, 11, 12]

print(Solution.sumOfThree(num=55))
