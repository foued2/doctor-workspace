from typing import List


class Solution:
    @staticmethod
    def maximumHappinessSum(happiness: List[int], k: int) -> int:
        # Sort the happiness list in descending order to get the highest values first
        happiness.sort(reverse=True)

        # Initialize the index to iterate over the happiness list
        i = 0

        # Initialize the result to accumulate the maximum happiness sum
        res = 0

        # Loop until we have selected 'k' elements
        while k > 0:
            # Update the current happiness value by reducing it with the index i
            # Use max to ensure the value doesn't go below 0
            happiness[i] = max(happiness[i] - i, 0)

            # Add the updated happiness value to the result
            res += happiness[i]

            # Move to the next index
            i += 1

            # Decrease k as we have selected one element
            k -= 1

        # Return the accumulated maximum happiness sum
        return res
