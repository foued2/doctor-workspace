from typing import List


class Solution:
    @staticmethod
    def restoreString(s: str, indices: List[int]) -> str:
        # Get the length of the input string
        n = len(s)

        # Initialize a list to store the characters in the original order
        res = [''] * n

        # Iterate over the characters in the shuffled string
        for i in range(n):
            # Place the character at index i in the shuffled string at its original position
            # as specified by the value at index i in the indices list
            res[indices[i]] = s[i]

        # Join the characters in the list to form the restored string
        return ''.join(res)


print(Solution.restoreString(s="codeleet", indices=[4, 5, 6, 7, 0, 2, 1, 3]))
