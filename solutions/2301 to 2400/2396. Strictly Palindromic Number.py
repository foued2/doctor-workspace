class Solution:
    @staticmethod
    def isStrictlyPalindromic(n: int) -> bool:
        # Store the original number to reset after each base conversion
        respawn = n

        # Iterate over each base from 2 to n-2
        for base in range(2, respawn - 1):
            camp = ''  # Initialize the string to store the converted number

            # Convert the number n to the current base
            while n:
                quotient, remainder = divmod(n, base)
                n = quotient
                camp += str(remainder)

            # Reverse the string to check if it's palindromic
            camp = camp[::-1]

            # Get the length of the converted string
            m = len(camp)

            # Check if the string is a palindrome
            for i in range(m // 2):
                if camp[i] != camp[m - i - 1]:
                    return False  # If not a palindrome, return False

            # Reset n to its original value for the next iteration
            n = respawn

        # If the number is palindromic in all bases, return True
        return True


print(Solution.isStrictlyPalindromic(n=9))
