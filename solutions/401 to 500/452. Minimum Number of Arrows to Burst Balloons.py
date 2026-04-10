from typing import List


class Solution:
    @staticmethod
    def findMinArrowShots(points: List[List[int]]) -> int:
        if not points:
            return 0

        # Sort the intervals based on the end point
        points.sort(key=lambda x: x[1])

        # Initialize variables
        end = points[0][1]
        arrows = 1

        # Iterate through the intervals
        for start, point in points:
            # If the start point is beyond the current end point, update end point and arrows count
            if start > end:
                arrows += 1
                end = point

        return arrows


# Test the findMinArrowShots function with provided intervals
print(Solution.findMinArrowShots(points=[[10, 16], [2, 8], [1, 6], [7, 12]]))
#
