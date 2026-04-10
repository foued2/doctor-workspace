from typing import List


class Solution:
    @staticmethod
    def findChampion(grid: List[List[int]]) -> int:
        # Initialize the highest score (champScore) to -1, which is less than any possible count of 1s
        champScore = -1
        # Initialize the index of the winner (winner) to 0
        winner = 0

        # Iterate over each row in the grid
        for i in range(len(grid)):
            # Count the number of 1s in the current row
            a = grid[i].count(1)

            # If the count of 1s in the current row is greater than or equal to the current champScore
            if champScore <= a:
                # Update champScore to the count of 1s in the current row
                champScore = a
                # Update the winner to the current row index
                winner = i

        # Return the index of the row with the highest count of 1s
        return winner


print(Solution.findChampion(grid=[[0, 1], [0, 0]]))
