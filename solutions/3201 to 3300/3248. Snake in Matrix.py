from typing import List


class Solution:
    @staticmethod
    def finalPositionOfSnake(n: int, commands: List[str]) -> int:
        # Initialize the final position variable
        ans = 0

        # Process each command to update the snake's position
        for command in commands:
            if command == "RIGHT":
                # Move one position to the right
                ans += 1
            if command == "LEFT":
                # Move one position to the left
                ans -= 1
            if command == "UP":
                # Move up one row (n positions back)
                ans -= n
            if command == "DOWN":
                # Move down one row (n positions forward)
                ans += n

        # Return the final position of the snake
        return ans


# Example usage
if __name__ == '__main__':
    print(Solution.finalPositionOfSnake(n=3, commands=["DOWN", "RIGHT", "UP"]))
    print(Solution.finalPositionOfSnake(n=2, commands=["RIGHT", "DOWN"]))