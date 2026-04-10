from typing import List


class Solution:
    @staticmethod
    def runningSum(nums: List[int]) -> List[int]:

        """
        This method calculates the running sum of the 1d array `nums`.
        """
        # Initialize the result list and the current sum variable
        #
        running_sum = []
        current_sum = 0

        # Iterate through each number in the given list
        for num in nums:
            # Update the current sum
            current_sum += num
            # Append the current sum to the running sum list
            running_sum.append(current_sum)

        # Return the running sum list
        return running_sum


if __name__ == '__main__':
    # Example usage
    print(Solution.runningSum([1, 2, 3, 4]))  # Output: [1, 3, 6, 10]
    print(Solution.runningSum([1, 1, 1, 1, 1]))  # Output: [1, 2, 3, 4, 5]
    print(Solution.runningSum([3, 1, 2, 10, 1]))  # Output: [3, 4, 6, 16, 17]


class Solution:
    @staticmethod
    def isDivisibleBySumAndProduct(n: int) -> bool:
        """
        Checks if n is divisible by the sum of its digits
        plus the product of its digits.
        """
        # We use a temporary variable so we don't lose the original n
        temp_n = n
        digit_sum = 0
        digit_prod = 1

        # Extract each digit one by one
        while temp_n > 0:
            digit = temp_n % 10  # Get the last digit
            digit_sum += digit  # Add it to our sum
            digit_prod *= digit  # Multiply it into our product
            temp_n //= 10  # Remove the last digit

        # Calculate the total divisor
        total = digit_sum + digit_prod

        # Return True if n is divisible by the total, else False
        return n % total == 0


if __name__ == '__main__':
    # Example usage
    print(Solution.isDivisibleBySumAndProduct(99))  # Output: True (9+9 + 9*9 = 99)
    print(Solution.isDivisibleBySumAndProduct(23))  # Output: False (2+3 + 2*3 = 11)