class Solution:
    @staticmethod
    def furthestDistanceFromOrigin(moves: str) -> int:
        # Count the number of 'L' moves
        left = moves.count('L')

        # Count the number of 'R' moves
        right = moves.count('R')

        # Calculate the number of moves that are neither 'L' nor 'R' (i.e., choice moves)
        choice = len(moves) - (left + right)

        # Calculate the furthest distance from the origin based on the counts of moves
        if left >= right:
            # If there are more 'L' moves, or they are equal, the choice moves can add to 'L' count
            ans = left + choice - right
        else:
            # If there are more 'R' moves, the choice moves can add to 'R' count
            ans = right + choice - left

        # Return the maximum distance from the origin
        return ans


print(Solution.furthestDistanceFromOrigin(moves="L_RL__R"))
