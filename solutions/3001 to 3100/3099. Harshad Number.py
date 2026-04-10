class Solution:
    @staticmethod
    def sumOfTheDigitsOfHarshadNumber(x: int) -> int:
        # Initialize a variable to store the sum of digits
        s = 0
        # Store the original number for later comparison
        original = x
        # Iterate through each digit of the number
        while x > 0:
            # Add the last digit to the sum
            s += x % 10
            # Remove the last digit from the number
            x //= 10
        # Check if the original number is divisible by the sum of its digits (Harshad number condition)
        if original % s == 0:
            # If it is, return the sum of the digits
            return s
        # If not, return -1
        return -1


if __name__ == '__main__':
    print(Solution.sumOfTheDigitsOfHarshadNumber(15646))
