from collections import defaultdict
from typing import List


class Solution:
    @staticmethod
    def findWinners(matches: List[List[int]]) -> List[List[int]]:
        # Initialize the result list with two empty lists: one for winners and one for players who lost exactly one
        # match.
        res = [[], []]

        # Track the number of losses for each player.
        losers_count = defaultdict(int)
        # Track all players who have participated in matches.
        all_players = set()

        # Iterate through each match.
        for match in matches:
            winner, loser = match
            # Add the winner and loser to the set of all players.
            all_players.add(winner)
            all_players.add(loser)
            # Increment the loss count for the loser.
            losers_count[loser] += 1

        # Identify players who have never lost.
        for player in all_players:
            if player not in losers_count:
                res[0].append(player)

        # Identify players who have lost exactly one match.
        for player, count in losers_count.items():
            if count == 1:
                res[1].append(player)

        # Sort the result lists for consistent output.
        res[0].sort()
        res[1].sort()

        return res


print(Solution.findWinners(matches=[[1, 3], [2, 3], [3, 6], [5, 6], [5, 7], [4, 5], [4, 8], [4, 9], [10, 4], [10, 9]]))
