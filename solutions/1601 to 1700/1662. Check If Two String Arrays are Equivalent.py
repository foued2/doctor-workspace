from typing import List


class Solution:
    @staticmethod
    def arrayStringsAreEqual(word1: List[str], word2: List[str]) -> bool:
        # Concatenate all strings in word1 into a single string
        word1 = "".join(word1)

        # Concatenate all strings in word2 into a single string
        word2 = "".join(word2)

        # Check if the concatenated strings are equal
        return word1 == word2


print(Solution.arrayStringsAreEqual(word1=["abc", "d", "defg"], word2=["abcddefg"]))
