class Solution:
    @staticmethod
    def trailingZeroes(n: int) -> int:
        # Initialize the result variable to count trailing zeroes
        res = 0

        # Loop until n is greater than or equal to 5, as factors of 5 contribute to trailing zeroes
        while n >= 5:
            # Divide n by 5 to count the number of times 5 appears as a factor
            n //= 5
            # Add the count of 5's to the result, as each 5 contributes a trailing zero
            res += n

        # Return the total count of trailing zeroes in n!
        return res
