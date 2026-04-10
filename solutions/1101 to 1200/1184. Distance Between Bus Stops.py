from typing import List


class Solution:
    @staticmethod
    def distanceBetweenBusStops(distance: List[int], start: int, destination: int) -> int:
        # Calculate the total mileage of the circular bus route
        mileage = sum(distance)

        # If start is greater than destination, swap them to simplify the calculation
        if start > destination:
            start, destination = destination, start

        # Calculate the distance when traveling clockwise from start to destination
        clockwise = sum(distance[start:destination])

        # Calculate the distance when traveling counter-clockwise
        # Since the route is circular, the counter-clockwise distance is the total mileage minus the clockwise distance
        counter_clockwise = mileage - clockwise

        # Determine the shorter distance between clockwise and counter-clockwise
        if clockwise <= counter_clockwise:
            ans = clockwise
        else:
            ans = counter_clockwise

        # Return the shortest distance
        return ans


print(Solution.distanceBetweenBusStops(distance=[1, 2, 3, 4], start=0, destination=3))
