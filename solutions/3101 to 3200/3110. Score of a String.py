class Solution:
    @staticmethod
    def scoreOfString(s: str) -> int:
        # Convert the string to a list of characters
        s = list(s)

        # Initialize the result variable to store the score
        res = 0

        # Initialize the index variable for iteration
        i = 0

        # Iterate through the string until the second-to-last character
        while i < len(s) - 1:
            # Calculate the absolute difference in ASCII values between consecutive characters
            difference = abs(ord(s[i]) - ord(s[i + 1]))

            # Add the absolute difference to the result
            res += difference

            # Move to the next pair of consecutive characters
            i += 1

        # Return the final score of the string
        return res


if __name__ == '__main__':
    # Test the scoreOfString method with input string "zaz"
    print(Solution.scoreOfString(s="zaz"))
