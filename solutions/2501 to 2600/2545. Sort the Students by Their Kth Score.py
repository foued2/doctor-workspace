from typing import List


class Solution:
    @staticmethod
    def sortTheStudents(score: List[List[int]], k: int) -> List[List[int]]:
        # Sort the list of student scores based on the k-th score in descending order
        score = sorted(score, key=lambda x: x[k], reverse=True)

        # Return the sorted list of scores
        return score


print(Solution.sortTheStudents(score=[[10, 6, 9, 1], [7, 5, 11, 2], [4, 8, 3, 15]], k=2))
