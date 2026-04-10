from typing import List


class Solution:
    @staticmethod
    def isWinner(player1: List[int], player2: List[int]) -> int:
        # Prepend a zero to both player scores to handle 1-based index easily
        player1 = [0] + player1
        player2 = [0] + player2

        # Calculate the number of rounds (including the prepended zero)
        n = len(player2)

        # Initialize the scores with the first round score (actual first round is at index 1)
        score1 = player1[1]
        score2 = player2[1]

        # Iterate over the scores starting from the second round (index 2)
        for i in range(2, n):
            # Check if the previous round or the round before that was a strike (10 points) for player1
            if player1[i - 1] == 10 or player1[i - 2] == 10:
                # If true, double the points for this round
                score1 += player1[i] * 2
            else:
                # Otherwise, add the points for this round
                score1 += player1[i]

            # Check if the previous round or the round before that was a strike (10 points) for player2
            if player2[i - 1] == 10 or player2[i - 2] == 10:
                # If true, double the points for this round
                score2 += player2[i] * 2
            else:
                # Otherwise, add the points for this round
                score2 += player2[i]

        # Determine the winner based on the total scores
        if score1 > score2:
            return 1  # Player 1 wins
        elif score1 < score2:
            return 2  # Player 2 wins
        else:
            return 0  # It's a tie


print(Solution.isWinner(player1=[2, 3], player2=[4, 1]))
