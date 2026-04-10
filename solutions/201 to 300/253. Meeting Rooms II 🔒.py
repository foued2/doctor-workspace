from typing import List


class Solution:
    @staticmethod
    def minMeetingRooms(intervals: List[List[int]]) -> int:
        # Sort the intervals based on their start times
        intervals.sort(key=lambda x: x[0])

        # Get the length of the intervals' list
        length = len(intervals)

        # Initialize the prefix sum to 1, assuming at least one meeting room is needed
        prefix_sum = 1

        # Iterate through the intervals
        for i in range(length - 1):
            # Check if the end time of the current interval overlaps with the start time of the next interval
            if intervals[i][1] > intervals[i + 1][0]:
                # If there's an overlap, increment the prefix sum to account for the additional meeting room needed
                prefix_sum += 1

        # Return the minimum number of meeting rooms required
        return prefix_sum


# Test the method
print(Solution.minMeetingRooms(intervals=[[0, 30], [5, 10], [15, 20]]))
