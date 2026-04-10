from typing import List


class Solution:
    @staticmethod
    def prefixCount(words: List[str], pref: str) -> int:
        # Initialize a count variable to store the number of words with the prefix
        count = 0

        # Iterate through each word in the list
        for word in words:
            # Check if the prefix of the word matches the specified prefix
            if word[:len(pref)] == pref:
                # If so, increment the count
                count += 1

        # Return the count of words with the specified prefix
        return count


print(Solution.prefixCount(words=["pay", "attention", "practice", "attend"], pref="at"))
