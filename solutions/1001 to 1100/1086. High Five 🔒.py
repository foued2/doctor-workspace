from collections import defaultdict  # Import defaultdict to create a dictionary with default list values
from typing import List  # Import List for type hinting


class Solution:
    @staticmethod
    def highFive(items: List[List[int]]) -> List[List[int]]:
        res = []  # Initialize an empty list to store the final results
        table = defaultdict(list)  # Create a defaultdict where each value is an empty list

        # Iterate over each pair of [id, score] in items
        for study in items:
            table[study[0]].append(study[1])  # Append the score to the list corresponding to the student's id

        # Iterate over each student's id and their list of scores
        for key, value in table.items():
            # Calculate the average score by summing the scores and dividing by the number of scores
            value = sum(value) // len(value)
            res.append([key, value])  # Append the [id, average_score] to the results list

        # Sort the results list by student id in ascending order
        res = sorted(res, key=lambda x: x[0])
        return res  # Return the final sorted results list


print(Solution.highFive(
    [[1, 91], [1, 92], [2, 93], [2, 97], [1, 60], [2, 77], [1, 65], [1, 87], [1, 100], [2, 100], [2, 76]]))
