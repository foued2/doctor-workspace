class Solution:
    @staticmethod
    def isSubsequence(s: str, t: str) -> bool:
        # Create a list of empty strings with the length of string s
        dp = ['' for _ in range(len(s))]

        # Initialize the starting index for string t
        start = 0

        # Iterate through each character in string s
        for i in range(len(s)):

            # Iterate through each character in string t starting from the current position 'start'
            for j in range(start, len(t)):

                # Check if the characters match and if the character is not present in dp[i:] (pruning)
                if s[i] == t[j] and s[i] not in dp[i:]:
                    # Add the character to dp
                    dp[i] = s[i]

                    # Update the starting index for the next iteration
                    start = j + 1

        # Join the characters in dp to form a string
        dp = ''.join(dp)

        # Check if dp is equal to string s
        return dp == s


print(Solution.isSubsequence(s="abc", t="ahbgdc"))
