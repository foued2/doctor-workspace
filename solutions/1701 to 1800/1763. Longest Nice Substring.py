class Solution:
    def longestNiceSubstring(self, s: str) -> str:
        """
        Inverted Sliding Window Algorithm, Recursion
        """
        # Base case: if the length of the string is less than 2, return an empty string
        if len(s) < 2:
            return ''

        # Create a set of characters seen in the current substring
        seen = set(s)

        # Iterate through each character of the string
        for i in range(len(s)):
            # Check if both the lowercase and uppercase versions of the current character are present in the substring
            if s[i].lower() in seen and s[i].upper() in seen:
                continue  # If both versions are present, continue to the next character

            # If one version is missing, divide the string into two substrings around the current character
            left = self.longestNiceSubstring(s[:i])  # Substring to the left of the current character
            right = self.longestNiceSubstring(s[i + 1:])  # Substring to the right of the current character

            # Return the longest "nice" substring among the left, right, and current substrings
            return max(left, right, key=len)

        # If all characters in the string are "nice", return the original string
        return s


# Test the solution
solution = Solution()
print(solution.longestNiceSubstring("YazaAay"))  # Output should be "aAa"
