from typing import List


class Solution:
    @staticmethod
    def nearestValidPoint(x: int, y: int, points: List[List[int]]) -> int:
        # Initialize the variable to store the index of the nearest valid point
        ans = -1
        # Initialize the minimum distance to a very large value
        min_distance = float('inf')

        # Iterate over the points with their indices
        for idx, point in enumerate(points):
            # Extract the x and y coordinates of the current point
            x1, y1 = point

            # Check if the point is valid (same x or same y as the given point)
            if x == x1 or y == y1:
                # Calculate the Manhattan distance from the given point
                manhattan_distance = abs(x1 - x) + abs(y1 - y)

                # If the calculated distance is less than the current minimum distance
                if manhattan_distance < min_distance:
                    # Update the minimum distance
                    min_distance = manhattan_distance
                    # Update the index of the nearest valid point
                    ans = idx
                # If the distance is the same as the current minimum, ensure the smallest index
                elif manhattan_distance == min_distance:
                    ans = min(ans, idx)

        # Return the index of the nearest valid point
        return ans


print(Solution.nearestValidPoint(x=3, y=4, points=[[1, 2], [3, 1], [2, 4], [2, 3], [4, 4]]))
