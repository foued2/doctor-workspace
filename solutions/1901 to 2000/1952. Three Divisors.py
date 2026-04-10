class Solution:
    @staticmethod
    def isThree(n: int) -> bool:
        # Initialize a variable to count the number of divisors
        div = 2  # We start with 2 because every number is divisible by 1

        # If n is less than 4, it cannot have 3 divisors
        if n < 4:
            return False

        # Iterate from 2 to n//2 (inclusive) to check for divisors
        for i in range(2, (n // 2) + 1):
            # If i is a divisor of n, increment the divisor count
            if n % i == 0:
                div += 1
                # If we find more than 3 divisors, return False
                if div == 4:
                    return False

        # If the loop completes and div equals 3, n has exactly 3 divisors
        return div == 3


print(Solution.isThree(9))
