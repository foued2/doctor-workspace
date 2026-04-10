from typing import List


class Solution:
    @staticmethod
    def countPrefixes(words: List[str], s: str) -> int:
        # Initialize a counter to keep track of the number of prefixes
        ans = 0
        # Iterate through each word in the list of words
        for word in words:
            # Check if the current word is a prefix of the string s
            if word == s[:len(word)]:
                # If it is a prefix, increment the counter
                ans += 1
        # Return the total count of prefixes
        return ans


# Example usage:
words = ["a", "b", "c", "ab", "bc", "abc"]
s = "abc"
result = Solution.countPrefixes(words, s)
print(result)  # Output should be 3, as "an", "ab", and "abc" are prefixes of "abc."
