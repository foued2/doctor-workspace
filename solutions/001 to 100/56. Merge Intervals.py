from typing import List


class Solution:
    @staticmethod
    def merge(intervals: List[List[int]]) -> List[List[int]]:
        if not intervals:
            return []

        # Sort intervals based on the start value
        intervals.sort(key=lambda x: x[0])

        merged = [intervals[0]]

        for interval in intervals[1:]:
            # If the current interval overlaps with the previous one, merge them
            if interval[0] <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], interval[1])
            else:
                # If no overlap, add the current interval to the merged list
                merged.append(interval)

        return merged

    print(merge(intervals=[[1, 3], [2, 6], [8, 10], [15, 18]]))
