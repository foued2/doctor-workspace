from typing import List


class Solution:
    @staticmethod
    def stringSequence(target: str) -> List[str]:
        res = []
        for char in target:
            sequence = ''
            letter = 'a'
            while letter != char:
                sequence += letter
                letter = chr(ord(letter) + 1)
                res.append(sequence)
            sequence += letter  # Add the target character
            res.append(sequence)
        return res

if __name__ == "__main__":
    solution = Solution()
    print(solution.stringSequence("abc"))
