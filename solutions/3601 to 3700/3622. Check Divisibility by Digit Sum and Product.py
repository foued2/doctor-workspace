# We define a class to match the expected LeetCode-style interface.
class Solution:
    # We mark this method as static because it does not use instance data.
    @staticmethod
    # We define the method that checks the divisibility rule for a number.
    def checkDivisibility(n: int) -> bool:
        # We start the sum of digits at 0 because we will add digits to it.
        digit_sum = 0
        # We start the product of digits at 1 because 1 is the neutral value for multiplication.
        digit_product = 1
        # We copy n into a temporary variable so we can change it while keeping the original.
        temp = n
        # We keep looping while there are still digits left in the temporary number.
        while temp > 0:
            # We separate the last digit and shrink the number using divmod.
            temp, digit = divmod(temp, 10)
            # We add the current digit to the running sum.
            digit_sum += digit
            # We multiply the running product by the current digit.
            digit_product *= digit
        # We check if n is divisible by the sum of (digit sum + digit product).
        return n % (digit_sum + digit_product) == 0
# We run example code only when this file is executed directly.
if __name__ == "__main__":
    # We test a number that should return True and print the result.
    print(Solution.checkDivisibility(132))  # True
    # We test a number that should return False and print the result.
    print(Solution.checkDivisibility(234))  # False
