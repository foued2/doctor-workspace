from typing import List


class Solution:
    @staticmethod
    def getLongestSubsequence(words: List[str], groups: List[int]) -> List[str]:
        # Initialize a list to store the longest subsequence of words
        dp = [words[0]]  # Initialize with the first word

        # Loop through each word starting from the second one
        for i in range(1, len(words)):
            # Check if the current word belongs to a different group than the previous one
            if groups[i] != groups[i - 1]:
                # If it belongs to a different group, append it to the longest subsequence
                dp.append(words[i])

        # Return the longest subsequence of words
        return dp


# Test the function
if __name__ == '__main__':
    words = ["a", "b", "c", "d", "e"]
    groups = [1, 1, 2, 2, 3]
    print(Solution.getLongestSubsequence(words, groups))  # Output: ['a', 'c', 'e']
