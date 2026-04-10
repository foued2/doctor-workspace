class Solution:
    @staticmethod
    def countOperations(num1: int, num2: int) -> int:
        """
        This method essentially uses the Euclidean algorithm to find the greatest common divisor (GCD) of num1 and
        num2.
        The number of operations needed corresponds to the quotient of num1 divided by num2 at each step of the
        algorithm, until num2 becomes zero, indicating that num1 is the GCD.
        """
        # Initialize a variable to store the number of operations
        ans = 0

        # Continue the loop until both num1 and num2 become 0
        while num1 and num2:
            # Ensure num1 is always greater than or equal to num2
            if num1 < num2:
                num1, num2 = num2, num1

            # Count how many times num2 can be subtracted from num1
            ans += num1 // num2

            # Update num1 to the remainder when divided by num2
            num1 %= num2

        # Return the total number of operations
        return ans


print(Solution.countOperations(num1=2, num2=3))
