from typing import List
from collections import Counter


class Solution:
    @staticmethod
    def bestHand(ranks: List[int], suits: List[str]) -> str:
        """
        Counting, Counter()
        """
        # Check if all suits are the same
        if len(set(suits)) == 1:
            return 'Flush'

        # Use Counter to count occurrences of each rank
        rank_count = Counter(ranks)

        # Check for "Three of a Kind" and "Pair"
        max_count = max(rank_count.values())
        if max_count >= 3:
            return "Three of a Kind"
        elif max_count == 2:
            return "Pair"

        # If neither "Flush", "Three of a Kind" nor "Pair", return "High Card"
        return "High Card"


# Example usage
solution = Solution()
ranks = [13, 2, 3, 1, 9]
suits = ['a', 'a', 'a', 'a', 'a']
print(solution.bestHand(ranks, suits))  # Output: "Flush"
