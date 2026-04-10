from typing import List


class Solution:
    @staticmethod
    def maxIceCream(costs: List[int], coins: int) -> int:
        # Initialize the count of ice creams bought
        ice_cream_count = 0

        # Determine the maximum cost of ice cream and create the count array
        max_cost = max(costs) + 1
        cost_count = [0] * max_cost

        # Count the occurrences of each cost
        for cost in costs:
            cost_count[cost] += 1

        # Iterate through the cost_count array to buy as many ice creams as possible
        for cost in range(1, max_cost):
            # Check if we can buy all ice creams of this cost
            if coins >= cost * cost_count[cost]:
                # Buy all ice creams of this cost
                ice_cream_count += cost_count[cost]
                # Deduct the total cost from the available coins
                coins -= cost * cost_count[cost]
            else:
                # Buy as many ice creams of this cost as possible
                ice_cream_count += coins // cost
                # No coins left to buy more ice creams
                break

        return ice_cream_count


# Example usage
solution = Solution()
print(solution.maxIceCream([1, 3, 2, 4, 1], 7))  # Expected output: 4
print(solution.maxIceCream([10, 6, 8, 7, 7, 8], 5))  # Expected output: 0
print(solution.maxIceCream([1, 6, 3, 1, 2, 5], 20))  # Expected output: 6
