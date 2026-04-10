from typing import List


class Solution:
    @staticmethod
    def minimumCost(cost: List[int]) -> int:
        # Calculate the total cost of all candies
        total = sum(cost)

        # Sort the costs in descending order
        cost.sort(reverse=True)

        # Initialize the total amount to be deducted for freebies
        freebies = 0

        # Iterate over the list, starting from the third element and skipping every two elements
        for i in range(2, len(cost), 3):
            # Add the cost of the third candy (freebie) in every triplet to the freebies' total
            freebies += cost[i]

        # Calculate the minimum cost by subtracting the total freebies from the total cost
        ans = total - freebies

        # Return the calculated minimum cost
        return ans


# Example usage:
costs = [1, 2, 3, 4, 5, 6]
result = Solution.minimumCost(costs)
print(result)  # Output should be 14, since the third, sixth candies are free.

print(Solution.minimumCost(cost=[10, 5, 9, 4, 1, 9, 10, 2, 10, 8]))
