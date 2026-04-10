from collections import Counter
from typing import List


class Solution:
    @staticmethod
    def makeEqual(words: List[str]) -> bool:
        # Concatenate all words into a single string
        s = ''
        for word in words:
            s += word

        # Count the frequency of each character in the concatenated string
        counter = Counter(s)

        # Number of words in the list
        num_words = len(words)

        # Check if each character's count is divisible by the number of words
        for value in counter.values():
            if value % num_words != 0:
                return False

        # If all character counts are divisible, return True
        return True


# Test case
words = ["abc", "aabc", "bc"]

# Create an instance of Solution and test the method
solution = Solution()
output = solution.makeEqual(words)
print(output)  # Expected: True

print(Solution.makeEqual(words=["ab", "a"]))
