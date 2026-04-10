from collections import Counter


class Solution:
    @staticmethod
    def checkAlmostEquivalent(word1: str, word2: str) -> bool:
        # Create a counter for word1 to count the frequency of each character
        table = Counter(word1)

        # Subtract the counts of characters in word2 from the counter
        table.subtract(word2)

        # Print the resulting counter (for debugging purposes)
        print(table)

        # Iterate through the values in the counter
        for value in table.values():
            # Check if the absolute difference of any character's count exceeds 3
            if abs(value) > 3:
                # If any character difference exceeds 3, the words are not almost equivalent
                return False

        # If no character difference exceeds 3, the words are almost equivalent
        return True


print(Solution.checkAlmostEquivalent(word1="abcdeef", word2="abaaacc"))
