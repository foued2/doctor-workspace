from typing import List


class Solution:
    @staticmethod
    def maxDistance(colors: List[int]) -> int:
        # Get the length of the list of colors
        n = len(colors)

        # Initialize the maximum distance to the right from the start
        right = 0

        # Initialize the maximum distance to the left from the end
        left = 0

        # Iterate from the end of the list to the start
        for i in range(n - 1, -1, -1):
            # Check if the current color is different from the first color
            if colors[i] != colors[0]:
                # If different, set the right distance to the current index (distance from the first element)
                right = abs(0 - i)
                break  # Exit the loop after finding the first different color

        # Iterate from the start of the list to the end
        for i in range(n):
            # Check if the current color is different from the last color
            if colors[i] != colors[-1]:
                # If different, set the left distance to the current distance (distance from the last element)
                left = abs(n - 1 - i)
                break  # Exit the loop after finding the first different color

        # Return the maximum of the two distances found
        return max(left, right)


print(Solution.maxDistance(colors=[4, 4, 4, 11, 4, 4, 11, 4, 4, 4, 4, 4]))
print(Solution.maxDistance([1, 1, 1, 6, 1, 1, 1]))
