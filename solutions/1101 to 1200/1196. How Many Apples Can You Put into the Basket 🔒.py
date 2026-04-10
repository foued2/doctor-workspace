from typing import List


class Solution:
    @staticmethod
    def maxNumberOfApples(weight: List[int]) -> int:
        # Sort the weights of the apples in ascending order
        weight.sort()

        # Initialize the number of apples that can be taken
        ans = 0
        # Initialize the capacity of the basket
        capacity = 5000

        # Loop through each weight in the sorted list
        for apple_weight in weight:
            # Check if adding the current apple would exceed the capacity
            if capacity >= apple_weight:
                # If not, subtract the weight of the apple from the capacity
                capacity -= apple_weight
                # Increment the count of apples taken
                ans += 1
            else:
                # If adding the current apple would exceed the capacity, break the loop
                break

        # Return the total number of apples that can be taken
        return ans


# Example usage:
weights = [100, 200, 150, 1000]
print(Solution.maxNumberOfApples(weights))  # Expected output: 4

weights = [900, 950, 800, 1000, 700, 800]
print(Solution.maxNumberOfApples(weights))  # Expected output: 5
