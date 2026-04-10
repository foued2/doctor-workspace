from typing import List


class Solution:
    @staticmethod
    def trap(height: List[int]) -> int:
        # Check if the list of heights is empty or contains only one element
        if not height or len(height) <= 1:
            return 0

        n = len(height)
        left_max = [0] * n  # List to store the maximum height encountered from the left side
        right_max = [0] * n  # List to store the maximum height encountered from the right side

        # Initialize the maximum height from the left side
        left_max[0] = height[0]
        for i in range(1, n):
            left_max[i] = max(left_max[i - 1], height[i])

        # Initialize the maximum height from the right side
        right_max[n - 1] = height[n - 1]
        for i in range(n - 2, -1, -1):
            right_max[i] = max(right_max[i + 1], height[i])

        water_trapped = 0  # Variable to store the total trapped water

        # Calculate the trapped water at each position
        for i in range(n):
            water_trapped += min(left_max[i], right_max[i]) - height[i]

        return water_trapped


if __name__ == '__main__':
    # Test the function with a sample input
    print(Solution.trap(height=[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))
