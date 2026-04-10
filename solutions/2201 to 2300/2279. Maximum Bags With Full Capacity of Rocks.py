from typing import List


class Solution:
    @staticmethod
    def maximumBags(capacity: List[int], rocks: List[int], additionalRocks: int) -> int:
        # Initialize the answer counter to zero
        ans = 0

        # Create a list to store the remaining capacity needed for each bag to be full
        bags = []

        # Iterate over the rocks and capacity lists to calculate the remaining capacity for each bag
        for i in range(len(rocks)):
            # Calculate the difference between capacity and current number of rocks in the bag
            remaining_capacity = capacity[i] - rocks[i]
            # Append the remaining capacity to the bags' list
            bags.append(remaining_capacity)

        # Sort the list of remaining capacities in ascending order
        bags.sort()

        # Iterate over the sorted list of remaining capacities
        for diff in bags:
            # Check if we have enough additional rocks to fill the current bag
            if additionalRocks >= diff:
                # If yes, increment the answer counter
                ans += 1
                # Subtract the number of rocks used to fill the current bag from additionalRocks
                additionalRocks -= diff
            else:
                # If not enough rocks are left to fill the current bag, break the loop
                break

        # Return the total number of bags that can be filled
        return ans


# Example usage:
capacity = [2, 3, 4, 5]
rocks = [1, 2, 4, 4]
additionalRocks = 2
print(Solution.maximumBags(capacity, rocks, additionalRocks))  # Expected output: 3

capacity = [10, 2, 2]
rocks = [2, 2, 0]
additionalRocks = 100
print(Solution.maximumBags(capacity, rocks, additionalRocks))  # Expected output: 3
