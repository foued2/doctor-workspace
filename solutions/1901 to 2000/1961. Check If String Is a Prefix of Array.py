from typing import List


class Solution:
    @staticmethod
    def isPrefixString(s: str, words: List[str]) -> bool:
        # Temporary string to build the prefix
        temp = ""
        # Iterate over the words and build the prefix
        for word in words:
            temp += word
            # Check if the current prefix matches s
            if temp == s:
                return True
        # Return False if s is not completely matched
        return False


print(Solution.isPrefixString(s="ccccccccc", words=["c", "cc"]))
