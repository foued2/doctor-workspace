class Solution:
    @staticmethod
    def longestPalindrome(s: str) -> int:
        # Check if the input string is empty
        if not s:
            return 0

        # Create a hash table to store character counts
        table = {}
        res = 0  # Initialize the result variable

        # Count occurrences of each character in the string
        for char in s:
            if char in table:
                table[char] += 1
            else:
                table[char] = 1

        center = False  # Flag to track whether a center character is used

        # Iterate through the hash table to make greedy choices
        for char_count in table.values():
            if char_count % 2 == 0:
                # Use all even counts directly in the palindrome
                res += char_count
            else:
                # Use (count - 1) characters for even palindrome length
                res += char_count - 1
                center = True  # Set the flag to indicate the use of a center character

        if center:
            res += 1  # Add 1 for the center character if used

        return res


# Test the function
print(Solution.longestPalindrome("abccccdd"))
