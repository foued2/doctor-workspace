from typing import List


class Solution:
    @staticmethod
    def minOperations(logs: List[str]) -> int:
        """
        Stack
        """
        # Initialize a stack to keep track of folder navigation
        stack = []

        # Iterate over each log entry in the logs list
        for log in logs:
            # If the log indicates moving up a directory
            if log == "../":
                # Pop from stack if it's not empty, simulating moving up a directory
                if stack:
                    stack.pop()
            # If the log indicates staying in the current directory, do nothing
            elif log == "./":
                continue
            # For any other log entry, which indicates moving into a new directory
            else:
                # Push the directory onto the stack
                stack.append(log)

        # The length of the stack represents the current depth in the folder structure
        return len(stack)


# Example usage:
logs = ["d1/", "d2/", "../", "d21/", "./"]
solution = Solution()
print(solution.minOperations(logs))  # Output: 2
