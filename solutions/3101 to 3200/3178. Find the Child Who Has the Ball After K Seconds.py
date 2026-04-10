class Solution:
    @staticmethod
    def numberOfChild(n: int, k: int) -> int:
        # Calculate the cycle length for ball movement from start to end and back to start
        cycle_length = 2 * (n - 1)

        # Calculate the effective steps within one full cycle
        effective_steps = k % cycle_length

        # Determine the position based on the effective steps
        if effective_steps < n:
            # If steps are less than n, the ball is moving to the right
            position = effective_steps
        else:
            # If steps are more than or equal to n, the ball is coming back to the left
            position = cycle_length - effective_steps

        return position


# Example usage
solution = Solution()
print(solution.numberOfChild(5, 7))  # Output: 3
print(solution.numberOfChild(5, 10))  # Output: 0
print(solution.numberOfChild(5, 15))  # Output: 4
