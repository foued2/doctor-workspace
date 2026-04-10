from typing import List


class Solution:
    @staticmethod
    def findWordsContaining(words: List[str], x: str) -> List[int]:
        # Use list comprehension to generate a list of indices for words containing the character x
        return [i for i, word in enumerate(words) if x in word]


print(Solution.findWordsContaining(words=["abc", "bcd", "aaaa", "cbc"], x="a"))
