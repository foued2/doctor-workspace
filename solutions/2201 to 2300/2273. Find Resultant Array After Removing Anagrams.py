from typing import List


class Solution:
    @staticmethod
    def removeAnagrams(words: List[str]) -> List[str]:
        # Initialize index i to start from the second word
        i = 1
        while i < len(words):
            # Check if the current word is an anagram of the previous word
            if sorted(words[i]) == sorted(words[i - 1]):
                # If they are anagrams, remove the current word
                words.pop(i)
            else:
                # If not, move to the next word
                i += 1
        return words


# Example usage:
sol = Solution()
print(sol.removeAnagrams(["abba", "baba", "bbaa", "cd", "cd"]))  # Expected output: ["abba", "cd"]
print(sol.removeAnagrams(["a", "b", "c", "d", "e"]))  # Expected output: ["a", "b", "c", "d", "e"]
print(sol.removeAnagrams(["ab", "ba", "abc", "cba", "cab"]))  # Expected output: ["ab", "abc"]

print(Solution.removeAnagrams(words=["abba", "baba", "bbaa", "cd", "cd"]))
