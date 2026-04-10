class Solution:
    @staticmethod
    def countDigits(num: int) -> int:
        # Initialize a counter for the number of divisible digits
        ans = 0
        # Make a copy of the original number to use for checking divisibility
        copy = num

        # Loop through each digit of the number
        while num:
            # Get the last digit of the number
            digit = num % 10
            # Check if the digit is not zero and the original number is divisible by this digit
            if digit != 0 and copy % digit == 0:
                # Increment the counter if the digit divides the number
                ans += 1
            # Remove the last digit from the number
            num //= 10

        # Return the total count of divisible digits
        return ans


# Example usage:
result = Solution.countDigits(120)
print(result)  # Output should be 2, as 1 and 2 divide 120, but 0 does not count.

print(Solution.countDigits(num=121))
