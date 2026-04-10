class Solution:
    @staticmethod
    def isArmstrong(n: int) -> bool:
        # Initialize the sum of digits raised to the power of the number of digits
        ans = 0

        # Convert the number to a string to easily iterate over each digit
        n_str = str(n)

        # Get the length of the number, which is the power each digit should be raised to
        k = len(n_str)

        # Iterate over each digit in the string representation of the number
        for digit in n_str:
            # Convert the digit back to an integer and raise it to the power of k, then add to the sum
            ans += int(digit) ** k

        # Convert the string representation back to an integer and compare it to the calculated sum
        return int(n_str) == ans


print(Solution.isArmstrong(123))
