from collections import Counter


class Solution:
    @staticmethod
    def maximumLengthSubstring(s: str) -> int:
        # Initialize the maximum length answer and the starting index of the sliding window
        ans = 0
        j = 0
        # Counter to keep track of character frequencies in the current window
        freq = Counter()

        # Iterate over the string with the ending index of the sliding window
        for i, ch in enumerate(s):
            # Increment the frequency count of the current character
            freq[ch] += 1

            # If the current character's frequency becomes 3, adjust the window
            while freq[ch] == 3:
                # Decrease the frequency of the character at the starting index
                freq[s[j]] -= 1
                # Move the starting index to the right
                j += 1

            # Update the maximum length of the valid substring
            ans = max(ans, i - j + 1)

        # Return the maximum length found
        return ans


print(Solution.maximumLengthSubstring("bcbbbcba"))
