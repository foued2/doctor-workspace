class Solution:
    @staticmethod
    def areNumbersAscending(s: str) -> bool:
        # Split the input string into tokens separated by spaces
        tokens = s.split(' ')

        # Initialize the variable to keep track of the last seen number
        current_number = -1  # Start with -1 to ensure any number is greater at the start

        # Iterate through each token in the split string
        for token in tokens:
            # Check if the token is a number
            if token.isdigit():
                # Convert the token to an integer
                number = int(token)

                # Check if the current number is less than or equal to the previous number
                if number <= current_number:
                    return False  # Return False if the numbers are not strictly increasing

                # Update the current number to the latest number
                current_number = number

        # If all numbers are in strictly increasing order, return True
        return True


# Example usage:
# Example string: "1 box has 3 blue 4 red 5 green and 7 yellow balls"
print(Solution.areNumbersAscending("1 box has 3 blue 4 red 5 green and 7 yellow balls"))  # Output: True

# Example string: "1 box has 3 blue 2 red 5 green and 7 yellow balls"
print(Solution.areNumbersAscending("1 box has 3 blue 2 red 5 green and 7 yellow balls"))  # Output: False

print(Solution.areNumbersAscending(s="sunset is at 7 51 pm overnight lows will be in the low 50 and 60 s"))
