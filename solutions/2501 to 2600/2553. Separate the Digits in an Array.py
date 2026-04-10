from typing import List


class Solution:
    @staticmethod
    def separateDigits(nums: List[int]) -> List[int]:
        # Initialize an empty list to store the result
        res = []

        # Iterate through each integer in the input list
        for x in nums:
            # Convert the integer to a string to separate the digits
            # Map each character back to an integer and convert to a list
            # Append the list of digits to the result list
            res += list(map(int, str(x)))

        # Return the final result list containing all separated digits
        return res


print(Solution.separateDigits(nums=[13, 25, 83, 77]))
