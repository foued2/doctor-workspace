from typing import List


class Solution:
    @staticmethod
    def numberOfEmployeesWhoMetTarget(hours: List[int], target: int) -> int:
        # Initialize a variable to count the employees who met the target
        count = 0

        # Iterate through each element in the 'hours' list
        for i in range(len(hours)):
            # Check if the hours worked by the current employee is greater than or equal to the target
            if hours[i] >= target:
                # If yes, increment the count
                count += 1

        # Return the count of employees who met the target
        return count


if __name__ == '__main__':
    print(Solution.numberOfEmployeesWhoMetTarget(hours=[0, 1, 2, 3, 4], target=2))
