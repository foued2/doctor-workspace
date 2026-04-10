from typing import List


class Solution:
    @staticmethod
    def isBoomerang(points: List[List[int]]) -> bool:
        # Extracting the coordinates for clarity
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]

        # Using the area method to check for collinearity,
        # This calculates the signed area of the triangle formed by the points
        # If the area is zero, the points are collinear
        area = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)

        # If the area is not zero, the points are not collinear and form a boomerang
        return area != 0


# Example usage
print(Solution.isBoomerang([[1, 1], [2, 3], [3, 2]]))  # Output: True
print(Solution.isBoomerang([[1, 1], [2, 2], [3, 3]]))  # Output: False
