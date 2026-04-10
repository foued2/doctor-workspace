from typing import List


class Solution:
    @staticmethod
    def minTimeToVisitAllPoints(points: List[List[int]]) -> int:
        # Initialize the total time to zero
        total_time = 0

        # Iterate through each pair of consecutive points
        for i in range(len(points) - 1):
            # Get the current point and the next point
            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            # Calculate the horizontal and vertical distances between the two points
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)

            # The time to move from one point to another is the maximum of these two distances
            # This is because you can move diagonally which covers both x and y in one move
            total_time += max(dx, dy)

        # Return the total time calculated
        return total_time


# Example usage:
points = [[1, 1], [3, 4], [-1, 0]]
print(Solution.minTimeToVisitAllPoints(points))  # Output should be 7

print(Solution.minTimeToVisitAllPoints(points=[[1, 1], [3, 4], [-1, 0]]))
