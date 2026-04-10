class Solution:
    @staticmethod
    def removeDigit(number: str, digit: str) -> str:
        # Initialize the answer as the smallest possible value.
        ans = '0'

        # Get the length of the input number.
        n = len(number)

        # Store the original number for resetting purposes.
        reset = number

        # Iterate over each character in the number.
        for i in range(n):
            # Check if the current character is the digit we want to remove.
            if number[i] == digit:
                # Remove the digit at the current position and form a new number.
                number = number[:i] + number[i + 1:]

                # Update the answer with the maximum value between the current answer and the new number.
                ans = max(ans, number)

            # Reset the number to its original value for the next iteration.
            number = reset

        # Iterate over each character in the number from the end to the beginning.
        for i in range(n - 1, -1, -1):
            # Check if the current character is the digit we want to remove.
            if number[i] == digit:
                # Remove the digit at the current position and form a new number.
                number = number[:i] + number[i + 1:]

                # Update the answer with the maximum value between the current answer and the new number.
                ans = max(ans, number)

            # Reset the number to its original value for the next iteration.
            number = reset

        # Return the answer which is the maximum possible value after removing the digit.
        return ans


print(Solution.removeDigit(number="133235431132", digit="3"))
