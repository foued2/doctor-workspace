from typing import List


class Solution:
    @staticmethod
    def numOfStrings(patterns: List[str], word: str) -> int:
        # Initialize the counter for patterns found in the word
        ans = 0

        # Iterate through each pattern in the patterns' list
        for pattern in patterns:
            # Check if the current pattern is a substring of the word
            if pattern in word:
                # If it is, increment the counter
                ans += 1

        # Return the total count of patterns found in the word
        return ans


print(Solution.numOfStrings(patterns=["a", "a", "a"], word="ab"))
