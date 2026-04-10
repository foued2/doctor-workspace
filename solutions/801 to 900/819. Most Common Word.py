from collections import defaultdict
from typing import List


class Solution:
    @staticmethod
    def mostCommonWord(paragraph: str, banned: List[str]) -> str:
        # Define symbols to be removed from the paragraph
        symbols = "!?',;."

        # Remove symbols and convert paragraph to lowercase
        for symbol in symbols:
            paragraph = paragraph.replace(symbol, ' ')

        # Split the paragraph into words
        words = paragraph.lower().split()

        # Create a defaultdict to count occurrences of each word
        counter = defaultdict(int)
        for word in words:
            counter[word] += 1

        # Remove banned words from the counter
        for word in banned:
            if word in counter:
                del counter[word]

        # Find the most common word
        max_count = 0
        most_common_word = ""
        for word, count in counter.items():
            if count > max_count:
                max_count = count
                most_common_word = word

        return most_common_word


print(Solution.mostCommonWord(paragraph="a, a, a, a, b,b,b,c, c", banned=["a"]))
