from typing import List


class Solution:
    @staticmethod
    def maxScoreWords(words: List[str], letters: List[str], score: List[int]) -> int:
        ans = 0
        alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                    'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ]
        paired = dict(zip(alphabet, score))
        for word in words:
            letters_removed = []
            word_score = 0
            for char in word:
                if char in letters:
                    word_score += paired[char]
                    ans += paired[char]
                    letters.remove(char)
                    letters_removed.append(char)
                else:
                    ans -= word_score
                    letters += letters_removed
                    break
        return ans


print(Solution.maxScoreWords(words=["dog", "cat", "dad", "good"], letters=["a", "a", "c", "d", "d", "d", "g", "o", "o"],
                             score=[1, 0, 9, 5, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
