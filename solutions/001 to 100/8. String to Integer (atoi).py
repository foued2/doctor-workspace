class Solution:
    @staticmethod
    def myAtoi(s: str) -> int:
        # Remove leading and trailing whitespaces
        s = s.strip()

        # Check if the string is empty after stripping whitespaces
        if not s:
            return 0

        # Initialize variables
        sign = 1  # Initialize sign as positive
        i = 0

        # Check for sign
        if s[i] == '-':
            sign = -1  # Update sign to negative if '-' is present
            i += 1
        elif s[i] == '+':
            i += 1

        # Initialize result
        result = 0

        # Iterate through the remaining characters of the string
        while i < len(s) and s[i].isdigit():
            # Convert character to integer and update result
            result = result * 10 + int(s[i])
            i += 1

        # Apply sign to result
        result *= sign

        # Check for integer overflow
        if result < -2 ** 31:
            return -2 ** 31
        elif result > 2 ** 31 - 1:
            return 2 ** 31 - 1
        else:
            return result
