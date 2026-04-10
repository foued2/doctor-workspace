class Solution:
    @staticmethod
    def countGoodSubstrings(s: str) -> int:
        # Convert the string into a list of characters for easier manipulation
        s = list(s)
        # Get the length of the string
        n = len(s)
        # Initialize the answer counter to zero
        ans = 0

        # Loop through the string with a sliding window of size 3
        for i in range(n - 2):
            # Create a substring of the current window of size 3
            substring = s[i:i + 3]
            # Convert the substring to a set to remove duplicates
            unique_chars = set(substring)
            # Check if the length of the set is 3, which means all characters are unique
            if len(unique_chars) == 3:
                # If yes, increment the answer counter
                ans += 1

        # Return the total count of good substrings
        return ans


# Example usage:
s = "xyzzaz"
print(Solution.countGoodSubstrings(s))  # Expected output: 1

s = "aababcabc"
print(Solution.countGoodSubstrings(s))  # Expected output: 4
