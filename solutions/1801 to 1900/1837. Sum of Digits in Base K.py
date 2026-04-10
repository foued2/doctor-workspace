class Solution:
    @staticmethod
    def sumBase(n: int, k: int) -> int:
        # Initialize the sum of digits to zero
        ans = 0

        # Loop until n becomes zero
        while n:
            # Compute quotient and remainder when dividing n by k
            quotient, remainder = divmod(n, k)

            # Add the remainder (current digit in base k) to the sum
            ans += remainder

            # Update n to the quotient for the next iteration
            n = quotient

        # Return the sum of the digits in base k
        return ans


# Example usage
solution = Solution()
result = solution.sumBase(34, 6)
print(result)  # Output: 9 (since 34 in base 6 is 54, and 5 + 4 = 9)

print(Solution.sumBase(n=34, k=6))
