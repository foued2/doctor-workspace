class Solution:
    @staticmethod
    def replaceDigits(s: str) -> str:
        # Get the length of the string
        n = len(s)

        # Convert the string to a list for mutable operations
        s = list(s)

        # Iterate over the string starting from index 1 with step 2 (i.e., all odd indices)
        for i in range(1, n, 2):
            # Replace the digit at the odd index with the character obtained by shifting the character
            # at the previous even index by the digit's value
            s[i] = chr(ord(s[i - 1]) + int(s[i]))

        # Join the list back into a string and return it
        return ''.join(s)


print(Solution.replaceDigits(s="a1c1e1"))
