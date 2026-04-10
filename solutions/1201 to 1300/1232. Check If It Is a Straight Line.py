from typing import List


class Solution:
    @staticmethod
    def checkStraightLine(coordinates: List[List[int]]) -> bool:
        # Number of coordinates
        n = len(coordinates)

        # If there are only two points, they always form a straight line
        if n == 2:
            return True

        # Calculate the initial slope using the first two points
        x0, y0 = coordinates[0]
        x1, y1 = coordinates[1]

        # Iterate over each pair of points and compare their slopes
        for i in range(2, n):
            x2, y2 = coordinates[i]
            # Using cross multiplication to check if slopes are equal:
            # (y1 - y0) * (x2 - x1) == (y2 - y1) * (x1 - x0)
            if (y1 - y0) * (x2 - x1) != (y2 - y1) * (x1 - x0):
                return False

        # If all slopes are equal, return True
        return True


print(Solution.checkStraightLine(coordinates=[[0, 0], [0, 1], [0, -1]]))
