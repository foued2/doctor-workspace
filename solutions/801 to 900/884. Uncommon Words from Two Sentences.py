from collections import Counter
from typing import List


class Solution:
    @staticmethod
    def uncommonFromSentences(s1: str, s2: str) -> List[str]:
        # Initialize an empty list to store the result
        res = []

        # Split both sentences into lists of words
        s1_words = s1.split(' ')
        s2_words = s2.split(' ')

        # Combine both lists of words and count occurrences using Counter
        table = Counter(s1_words + s2_words)

        # Iterate through the Counter dictionary
        for word, count in table.items():
            # If the word appears exactly once, add it to the result list
            if count == 1:
                res.append(word)

        # Return the list of uncommon words
        return res


print(Solution.uncommonFromSentences(s1="this apple is sweet", s2="this apple is sour"))
