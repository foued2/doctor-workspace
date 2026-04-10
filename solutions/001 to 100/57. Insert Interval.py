from typing import List


class Solution:
    @staticmethod
    def insert(intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        # Initialize an empty list to store the result
        merged_intervals = []
        # Initialize a variable to track whether newInterval is inserted
        new_interval_inserted = False
        # Iterate through each interval in the list
        for interval in intervals:
            # If newInterval is already inserted or the end of the current interval is before the start of newInterval
            if new_interval_inserted or interval[1] < newInterval[0]:
                merged_intervals.append(interval)
            # If the end of newInterval is before the start of the current interval
            elif interval[0] > newInterval[1]:
                # Insert newInterval before the current interval
                merged_intervals.append(newInterval)
                # Append the current interval
                merged_intervals.append(interval)
                # Set new_interval_inserted to True
                new_interval_inserted = True
            # If there is an overlap between newInterval and the current interval
            else:
                # Merge the intervals by updating the start and end of newInterval
                newInterval[0] = min(newInterval[0], interval[0])
                newInterval[1] = max(newInterval[1], interval[1])
        # If newInterval is not inserted yet, append it to the result
        if not new_interval_inserted:
            merged_intervals.append(newInterval)
        return merged_intervals


# Test the insert function with provided intervals and newInterval
print(Solution.insert(intervals=[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], newInterval=[4, 8]))
