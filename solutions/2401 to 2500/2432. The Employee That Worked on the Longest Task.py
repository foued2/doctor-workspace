from typing import List


class Solution:
    @staticmethod
    def hardestWorker(n: int, logs: List[List[int]]) -> int:
        # Initialize the answer with the first worker's ID
        ans = logs[0][0]

        # Initialize the maximum time taken with the time taken by the first worker
        max_time = logs[0][1]

        # Iterate over the logs starting from the second log
        for i in range(1, len(logs)):
            # Current worker's ID
            id = logs[i][0]

            # Calculate the time taken for the current task
            task_time = logs[i][1] - logs[i - 1][1]

            # If the current task time is greater than the maximum recorded time
            if task_time > max_time:
                # Update the maximum time
                max_time = task_time

                # Update the answer to the current worker's ID
                ans = id
            # If the current task time is equal to the maximum recorded time
            elif task_time == max_time:
                # Update the answer to the smallest worker's ID in case of a tie
                ans = min(id, ans)

        # Return the worker's ID who worked the hardest
        return ans


print(Solution.hardestWorker(n=10, logs=[[0, 3], [2, 5], [0, 9], [1, 15]]))
