class Solution:
    @staticmethod
    def numberOfMatches(n: int) -> int:
        # Initialize a variable to store the total number of matches played
        total_matches = 0

        # Continue the loop until there is only one team left
        while n != 1:
            # If the number of teams is even, each team plays against another team
            if n % 2 == 0:
                # Calculate the number of matches played in this round and update the total matches
                matches_this_round = n / 2
                total_matches += matches_this_round

                # Update the number of teams for the next round
                n /= 2
            else:
                # If the number of teams is odd, one team gets a bye and advances to the next round
                # The remaining teams play against each other
                matches_this_round = (n - 1) / 2
                total_matches += matches_this_round

                # Update the number of teams for the next round
                n = ((n - 1) / 2) + 1

        # Return the total number of matches played
        return int(total_matches)


print(Solution.numberOfMatches(1000))

