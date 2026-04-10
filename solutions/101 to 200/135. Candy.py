from typing import List


class Solution:
    @staticmethod
    def candy(ratings: List[int]) -> int:
        n = len(ratings)
        if n == 0:
            return 0

        # Initialize candies array with 1 candy for each child
        candies = [1] * n

        # Forward pass: Adjust candies from left to right
        for i in range(1, n):
            if ratings[i] > ratings[i - 1]:
                candies[i] = candies[i - 1] + 1

        # Backward pass: Adjust candies from right to left
        for i in range(n - 2, -1, -1):
            if ratings[i] > ratings[i + 1]:
                candies[i] = max(candies[i], candies[i + 1] + 1)

        # Total candies needed is the sum of candies for each child
        return sum(candies)


# Test the solution with the provided example
print(Solution.candy(ratings=[1, 0, 2]))
