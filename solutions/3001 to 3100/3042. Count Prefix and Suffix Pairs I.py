from typing import List


class Solution:
    @staticmethod
    def countPrefixSuffixPairs(words: List[str]) -> int:
        # Define a helper function to check if a word is both a prefix and a suffix of another word
        def is_prefix_suffix(prefix, word):
            # Check if 'prefix' is a prefix of 'word'
            is_prefix = word.startswith(prefix)
            # Check if 'prefix' is a suffix of 'word'
            is_suffix = word.endswith(prefix)
            # Return True if both conditions are met, otherwise return False
            return is_prefix and is_suffix

        # Initialize a counter to count the number of valid (i, j) pairs
        count = 0

        # Iterate over all possible pairs of indices (i, j)
        for i in range(len(words)):
            for j in range(len(words)):
                # Ensure that i < j to avoid duplicate pairs and self-comparison
                if i < j and is_prefix_suffix(words[i], words[j]):
                    # Increment the count if words[i] is both a prefix and a suffix of words[j]
                    count += 1

        # Return the final count of valid pairs
        return count


# Example usage
print(Solution.countPrefixSuffixPairs(words=["a", "aba", "ababa", "aa"]))  # Expected output based on logic
