"""
Dynamic Programming (DP) using Memorization (dp table) approach and sub-problems
"""


class Solution:
    @staticmethod
    def longestPalindrome(s: str) -> str:
        """
        :param s:
        :return:
        """
        n = len(s)

        # Create a table for memoization
        dp = [[False] * n for _ in range(n)]

        # All substrings of length 1 are palindromes
        for i in range(n):
            dp[i][i] = True

        start, max_length = 0, 1

        # Check substrings of length 2
        for i in range(n - 1):
            if s[i] == s[i + 1]:
                dp[i][i + 1] = True
                start = i
                max_length = 2

        # Check substrings of length 3 and above
        for length in range(3, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if dp[i + 1][j - 1] and s[i] == s[j]:
                    dp[i][j] = True
                    start = i
                    max_length = length

        return s[start:start + max_length]

    print(longestPalindrome("madam"))
