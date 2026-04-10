class Solution:
    @staticmethod
    def addDigits(num: int) -> int:
        # Continue processing while num has more than one digit
        while num > 9:
            res = 0
            # Sum all digits of num
            while num:
                res += num % 10  # Add the last digit of num to res
                num //= 10  # Remove the last digit from num
            num = res  # Update num to be the sum of its digits
        return num  # Return the single-digit result


if __name__ == '__main__':
    # Example usage: For the input 38,
    # 3 + 8 = 11 (first iteration), 1 + 1 = 2 (second iteration)
    # The result is 2.
    print(Solution().addDigits(38))


class Solution:
    @staticmethod
    def addDigits(num: int) -> int:
        """
        Using the digital root formula, Number theory
        """
        # Applying the digital root formula using modular arithmetic
        return 1 + (num - 1) % 9 if num > 0 else 0


if __name__ == '__main__':
    # Example usage
    print(Solution().addDigits(252))  # Output should be 2