from typing import List


class Solution:
    @staticmethod
    def stringMatching(words: List[str]) -> List[str]:
        """
        Naive string matching to find all words that are substrings of other words.
        """
        n = len(words)
        res = set()  # Use a set to avoid duplicate results

        for i in range(n):
            for j in range(n):
                if i != j and words[i] in words[j]:
                    res.add(words[i])

        return list(res)


# Example usage
print(Solution.stringMatching(words=["mass", "as", "hero", "superhero"]))


class Solution:
    @staticmethod
    def kmp_search(text: str, pattern: str) -> bool:
        """
        Use KMP algorithm to check if 'pattern' is a substring of 'text'.
        """
        # Step 1: Build the LPS (Longest Prefix Suffix) array
        def build_lps(pattern: str) -> List[int]:
            lps = [0] * len(pattern)  # LPS array initialization
            length = 0  # Length of the previous longest prefix suffix
            i = 1  # Start from the second character in the pattern

            while i < len(pattern):
                if pattern[i] == pattern[length]:
                    length += 1
                    lps[i] = length
                    i += 1
                else:
                    if length != 0:
                        length = lps[length - 1]
                    else:
                        lps[i] = 0
                        i += 1
            return lps

        # Step 2: Perform KMP search using the LPS array
        lps = build_lps(pattern)  # Build LPS array for the pattern

        i = 0  # Index for text
        j = 0  # Index for the pattern

        while i < len(text):
            if pattern[j] == text[i]:
                i += 1
                j += 1

            if j == len(pattern):  # Found the pattern in text
                return True
            elif i < len(text) and pattern[j] != text[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1

        return False  # Pattern not found in text

    def stringMatching(self, words: List[str]) -> List[str]:
        """
        Find all strings in the array that are substrings of another string in the array.
        """
        result = []

        # Step 3: Iterate over each word in the list and check if it is a substring of any other word
        for i in range(len(words)):
            for j in range(len(words)):
                if i != j and self.kmp_search(words[j], words[i]):
                    result.append(words[i])
                    break

        return result


# Example usage
solution = Solution()
words = ["mass", "as", "hero", "superhero"]
print(solution.stringMatching(words))  # Output: ["as", "hero"]
