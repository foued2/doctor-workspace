from typing import List
import heapq


class Solution:
    @staticmethod
    def findRelativeRanks(score: List[int]) -> List[str]:
        # Create a dictionary to map scores to their indices
        score_map = {}
        for i, s in enumerate(score):
            score_map[s] = i

        # Sort the scores in descending order
        sorted_scores = sorted(score, reverse=True)

        # Initialize a result list to store the ranks
        result = [""] * len(score)

        # Assign ranks
        for rank, s in enumerate(sorted_scores):
            index = score_map[s]
            if rank == 0:
                result[index] = "Gold Medal"
            elif rank == 1:
                result[index] = "Silver Medal"
            elif rank == 2:
                result[index] = "Bronze Medal"
            else:
                result[index] = str(rank + 1)

        return result


# Test the Solution class with the provided test case
solution = Solution()
score = [123123, 11921, 1, 0, 123]
print(solution.findRelativeRanks(score))  # Output: ["Gold Medal", "Silver Medal", "4", "5", "Bronze Medal"]


class Solution:
    @staticmethod
    def findRelativeRanks(score: List[int]) -> List[str]:
        # Create a max heap to store scores along with their indices
        max_heap = [(-s, i) for i, s in enumerate(score)]
        heapq.heapify(max_heap)

        # Initialize a result list to store the ranks
        result = [""] * len(score)

        # Assign ranks
        for rank in range(1, len(score) + 1):
            neg_score, index = heapq.heappop(max_heap)
            if rank == 1:
                result[index] = "Gold Medal"
            elif rank == 2:
                result[index] = "Silver Medal"
            elif rank == 3:
                result[index] = "Bronze Medal"
            else:
                result[index] = str(rank)

        return result


# Test the Solution class with the provided test case
solution = Solution()
score = [123123, 11921, 1, 0, 123]
print(solution.findRelativeRanks(score))  # Output: ["Gold Medal", "Silver Medal", "4", "5", "Bronze Medal"]
