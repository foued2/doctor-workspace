from typing import List


class Solution:
    # Constant to represent the initial value for the answer
    INITIAL_ANSWER = 0

    @staticmethod
    def taskSchedulerII(tasks: List[int], space: int) -> int:
        """
        Hash Table
        """
        # Initialize the current day counter
        current_day = Solution.INITIAL_ANSWER
        # Dictionary to keep track of the last day each task was executed
        last_executed_day = {}

        for task in tasks:
            # Check if the task has been executed before
            if task in last_executed_day:
                # Calculate the next available day the task can be executed considering the space
                next_available_day = last_executed_day[task] + space + 1
                # If the current day is less than the next available day, adjust the current day
                if current_day <= last_executed_day[task] + space:
                    current_day = next_available_day

            # Update the last day this task was executed
            last_executed_day[task] = current_day
            # Move to the next day
            current_day += 1

            # Return the total number of days required to complete tasks
        return current_day


if __name__ == '__main__':
    # Test cases
    print(Solution().taskSchedulerII(tasks=[5, 8, 8, 5], space=2))  # Output: 6
    print(Solution().taskSchedulerII(tasks=[1, 2, 1, 2, 3, 1], space=3))  # Output: 9