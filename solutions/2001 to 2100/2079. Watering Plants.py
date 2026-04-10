from typing import List


class Solution:
    @staticmethod
    def wateringPlants(plants: List[int], capacity: int) -> int:
        # Initialize the number of steps taken to 0
        ans = 0

        # Store the original capacity for refilling purposes
        refill_capacity = capacity

        # Iterate through each plant
        for i in range(len(plants)):
            # Check if the current capacity is enough to water the plant
            if capacity >= plants[i]:
                ans += 1  # Step forward to water the plant
                capacity -= plants[i]  # Reduce the capacity by the amount of water used
            else:
                # Refill the can and walk back to the river (i steps forward + i steps back)
                ans += 2 * i + 1  # 2*i for walking back and forth, 1 for stepping to the plant
                capacity = refill_capacity - plants[i]  # Refill and water the current plant

        return ans  # Return the total number of steps taken


# Example usage:
sol = Solution()
print(sol.wateringPlants([2, 4, 5, 1, 2], 6))  # Output should be the number of steps needed

print(Solution.wateringPlants(plants=[2, 2, 3, 3], capacity=5))
