import math
from typing import List


class Solution:
    @staticmethod
    def findGCD(nums: List[int]) -> int:
        # Sort the list of numbers to ensure the minimum and maximum numbers are at the beginning and end
        nums = sorted(nums)

        # Calculate the GCD of the minimum and maximum numbers
        return math.gcd(nums[0], nums[-1])


print(Solution.findGCD(nums=[7, 5, 6, 8, 3]))
