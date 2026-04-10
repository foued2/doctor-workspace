class Solution:
    @staticmethod
    def makeSmallestPalindrome(s: str) -> str:
        # Get the length of the string
        n = len(s)
        # Convert the string into a list of characters for easy modification
        s = list(s)
        # Initialize two pointers, i at the start and j at the end of the list
        i, j = 0, n - 1

        # Loop until the two pointers meet in the middle
        while i < j:
            # If the character at the start pointer is less than the character at the end pointer
            if s[i] < s[j]:
                # Set the character at the end pointer to be the same as the character at the start pointer
                s[j] = s[i]
            else:
                # Otherwise, set the character at the start pointer to be the same as the character at the end pointer
                s[i] = s[j]
            # Move the start pointer forward
            i += 1
            # Move the end pointer backward
            j -= 1

        # Convert the list of characters back into a string and return it
        return ''.join(s)


print(Solution.makeSmallestPalindrome(s="abcd"))
