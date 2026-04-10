from typing import List


class Solution:
    @staticmethod
    def isAcronym(words: List[str], s: str) -> bool:
        # Extract the first character of each word in the list
        res = [word[0] for word in words]

        # Concatenate the characters to form a potential acronym
        acronym = ''.join(res)

        # Check if the potential acronym matches the provided string
        return acronym == s


if __name__ == '__main__':
    print(Solution.isAcronym(["never", "gonna", "give", "up", "on", "you"], s="ngguoy"))
