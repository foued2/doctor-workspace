from typing import List


class Solution:
    @staticmethod
    def haveConflict(event1: List[str], event2: List[str]) -> bool:
        # Extract the start and end times of the first event
        start1, end1 = event1
        # Extract the start and end times of the second event
        start2, end2 = event2

        # Check if the first event starts before the second event ends
        # and if the first event ends after the second event starts
        # If both conditions are true, the events overlap
        return start1 <= end2 and end1 >= start2


# Example usage:
event1 = ["01:00", "02:00"]
event2 = ["01:30", "02:30"]
solution = Solution()
print(solution.haveConflict(event1, event2))  # Output: True, as the events overlap between 01:30 and 02:00

print(Solution.haveConflict(event1=["10:00", "11:00"], event2=["14:00", "15:00"]))
