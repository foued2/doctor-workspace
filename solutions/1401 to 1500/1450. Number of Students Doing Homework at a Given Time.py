from typing import List


class Solution:
    @staticmethod
    def busyStudent(startTime: List[int], endTime: List[int], queryTime: int) -> int:
        # Initialize a variable to store the count of busy students
        res = 0

        # Iterate through the range of indices of the lists
        for i in range(len(startTime)):
            # Check if the queryTime falls within the time slot of the student's activity
            if endTime[i] >= queryTime >= startTime[i]:
                # If yes, increment the count of busy students
                res += 1

        # Return the count of busy students
        return res


if __name__ == '__main__':
    print(Solution.busyStudent(startTime=[4], endTime=[4], queryTime=4))
