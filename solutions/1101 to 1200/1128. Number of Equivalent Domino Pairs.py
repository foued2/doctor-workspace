from collections import defaultdict
from typing import List


class Solution:
    @staticmethod
    def numEquivDominoPairs(dominoes: List[List[int]]) -> int:
        # Initialize the answer to 0
        ans = 0
        # Initialize a defaultdict with int, which defaults to 0 for any missing keys
        table = defaultdict(int)

        # Iterate over each domino piece in the dominoes list
        for piece in dominoes:
            # Sort the tuple to handle both orientations (e.g., [1, 2] and [2, 1])
            piece = tuple(sorted(piece))

            # Increment the count of this sorted piece in the table
            table[piece] += 1

        # Iterate over the counts in the table to calculate the number of pairs
        for value in table.values():
            # If there are at least 2 identical pieces, count the pairs
            if value >= 2:
                # The number of pairs that can be formed from `value` pieces is given by nC2 = n * (n - 1) / 2
                ans += (value * (value - 1)) // 2

        # Return the total number of equivalent domino pairs
        return ans


# Example usage:
dominoes = [[1, 2], [2, 1], [3, 4], [5, 6]]
print(Solution.numEquivDominoPairs(dominoes))  # Output: 1


print(Solution.numEquivDominoPairs(dominoes=[[1, 2], [2, 1], [3, 4], [5, 6]]))
