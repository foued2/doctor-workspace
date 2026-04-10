from typing import List


class Solution:
    @staticmethod
    def largestAltitude(gain: List[int]) -> int:
        # Get the number of elements in the gain list
        n = len(gain)

        # Initialize the highest altitude to 0 as we start from sea level
        highest_altitude = 0

        # Initialize the current altitude to 0 as we start from sea level
        altitude = 0

        # Iterate through each gain value to calculate the current altitude
        for i in range(n):
            # Update the current altitude by adding the gain at index i
            altitude += gain[i]

            # Update the highest altitude if the current altitude is greater
            highest_altitude = max(highest_altitude, altitude)

        # Return the highest altitude reached during the hike
        return highest_altitude


print(Solution.largestAltitude(gain=[-4, -3, -2, -1, 4, 3, 2]))
