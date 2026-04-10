from typing import List


class Solution:
    @staticmethod
    def canAliceWin(nums: List[int]) -> bool:
        # Initialize the sums for single-digit numbers and double-digit numbers
        sum_single = 0
        sum_double = 0

        # Iterate over all numbers in the input list
        for num in nums:
            # If the number is a single-digit number (less than 10), add it to sum_single
            if num < 10:
                sum_single += num
            # If the number is a double-digit number (10 or greater), add it to sum_double
            else:
                sum_double += num

        # Return True if the sums of single-digit and double-digit numbers are not equal
        return sum_double != sum_single


if __name__ == '__main__':
    # Example usage of the function to check if Alice can win
    # Prints the result of canAliceWin for the list [1, 1, 2, 2, 2, 10]
    # This will output True because sum_double (10) is not equal to sum_single (8)
    print(Solution().canAliceWin([1, 1, 2, 2, 2, 10]))