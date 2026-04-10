class Solution:
    @staticmethod
    def countEven(num: int) -> int:
        # Calculate the sum of digits of the given number
        digit_sum = sum(int(digit) for digit in str(num))

        # If the sum of digits is even, we include num itself
        if digit_sum % 2 == 0:
            # Half of the numbers up to num will have even sums
            return num // 2
        else:
            # If the sum is odd, exclude num itself and half of the rest will be even
            return (num - 1) // 2


# Example usage:
# num = 30
# The function will count the number of integers from 1 to 30 with even digit sums
print(Solution.countEven(30))  # Output: 14

print(Solution.countEven(num=28))
