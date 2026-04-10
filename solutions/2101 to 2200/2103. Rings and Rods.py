from collections import defaultdict


class Solution:
    @staticmethod
    def countPoints(rings: str) -> int:
        # Initialize the counter for the total points
        ans = 0

        # Initialize a dictionary to store the colors associated with each rod
        # Using default dict with sets as the default factory to avoid manual checks for key existence
        game = defaultdict(set)

        # Iterate through the rings in the input string
        for i in range(0, len(rings), 2):
            # Extract the current ring and its color and rod
            ring = rings[i:i + 2]
            color, rod = ring[0], ring[1]

            # Add the color to the set associated with the rod in the game dictionary
            game[rod].add(color)

        # Iterate through the sets of colors associated with each rod
        for rod_colors in game.values():
            # Check if the length of the set is equal to 3, indicating all three colors are present
            if len(rod_colors) == 3:
                # Increment the counter for the total points
                ans += 1

        # Return the total points
        return ans


print(Solution.countPoints(rings="B0B6G0R6R0R6G9"))
