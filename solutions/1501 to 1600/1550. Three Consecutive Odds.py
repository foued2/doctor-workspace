from typing import List


class Solution:
    @staticmethod
    def threeConsecutiveOdds(arr: List[int]) -> bool:
        # Initialize a counter to track consecutive odd numbers
        count = 0

        # Iterate through each number in the array
        for num in arr:
            # Check if the current number is odd
            if num % 2 != 0:
                # Increment the count of consecutive odd numbers
                count += 1
            else:
                # Reset the count if the number is even
                count = 0

            # Check if we have found three consecutive odd numbers
            if count == 3:
                return True

        # Return False if no three consecutive odd numbers are found
        return False


# Example usage
print(Solution.threeConsecutiveOdds([2, 6, 4, 1]))  # Expected output: False
print(Solution.threeConsecutiveOdds([1, 2, 34, 3, 4, 5, 7, 23]))  # Expected output: True
print(Solution.threeConsecutiveOdds([1, 3, 5, 7]))  # Expected output: True
print(Solution.threeConsecutiveOdds([1, 3, 2, 4, 5, 7]))  # Expected output: False
