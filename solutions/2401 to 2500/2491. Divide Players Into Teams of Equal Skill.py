import math
from typing import List


class Solution:
    @staticmethod
    def dividePlayers(skill: List[int]) -> int:
        # Initialize the answer to hold the sum of chemistries
        ans = 0
        # List to store each formed team (pair)
        res = []
        # Get the number of players
        n = len(skill)
        # Sort the skills to facilitate pairing
        skill.sort()

        # Iterate through the first half of the sorted skills list
        for i in range(n // 2):
            # Form a team by pairing the ith smallest and ith largest skill
            team = [skill[i], skill[n - i - 1]]
            # Calculate the chemistry of the team as the product of the two skills
            chemistry = math.prod(team)

            # If res is not empty, check if the sum of current team skills equals the sum of the last team skills
            if res and sum(team) != sum(res[-1]):
                # If not, return -1 indicating teams cannot be balanced
                return -1
            else:
                # Append the team to the results list
                res.append(team)

            # Add the team's chemistry to the total answer
            ans += chemistry

        # Return the total sum of all chemistries
        return ans


# Example usage:
skill = [1, 2, 3, 4, 5, 6]
solution = Solution()
print(solution.dividePlayers(skill))  # Output: 44

print(Solution.dividePlayers(skill=[3, 2, 5, 1, 3, 4]))
