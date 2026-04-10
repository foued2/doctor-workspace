from typing import List


class Solution:
    @staticmethod
    def countConsistentStrings(allowed: str, words: List[str]) -> int:
        # Initialize the count of inconsistent strings to zero
        count = 0

        # Convert the allowed characters string to a set for O(1) lookup time
        a = set(allowed)

        # Iterate through each word in the list of words
        for i in words:
            # Iterate through each character in the current word
            for j in i:
                # Check if the character is not in the allowed set
                if j not in allowed:
                    # Increment the count of inconsistent strings
                    count += 1
                    # Break the inner loop as we found an inconsistent character
                    break

        # Return the count of consistent strings by subtracting the count of inconsistent strings from total words
        return len(words) - count


print(Solution.countConsistentStrings(allowed="abc", words=["a", "b", "c", "ab", "ac", "bc", "abc"]))
