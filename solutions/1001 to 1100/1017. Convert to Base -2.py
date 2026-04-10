class Solution:
    @staticmethod
    def baseNeg2(n: int) -> str:
        """
        Convert a given integer to negative base-2 string.
        """
        # Edge Case: If the input number is zero, return "0"
        if n == 0:
            return "0"

        # Initialize an empty list to store the result digits
        result = []

        # Process the number until it reduces to zero
        while n != 0:
            # Perform integer division of n by -2 and store both quotient and remainder
            n, remainder = divmod(n, -2)

            # If the remainder is negative, adjust the remainder and quotient
            if remainder < 0:
                remainder += 2  # Correct the remainder by adding 2
                n += 1  # Compensate the division by increasing n

            # Append the adjusted remainder as a string to the result list
            result.append(str(remainder))

        # The result list will have the digits in reverse order, reverse and join them to form the final string
        return ''.join(result[::-1])


# Test the function
if __name__ == '__main__':
    # Testing the function with input 3 which should output '111'
    print(Solution.baseNeg2(258))