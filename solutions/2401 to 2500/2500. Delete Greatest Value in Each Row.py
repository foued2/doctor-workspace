from typing import List


class Solution:
    @staticmethod
    def deleteGreatestValue(grid: List[List[int]]) -> int:
        # Initialize the answer accumulator to 0
        ans = 0
        # Determine the number of rows
        m = len(grid)

        # Continue as long as there are non-empty rows
        while any(grid):
            # Initialize the maximum value of this iteration
            max_row = 0
            # Iterate over each row
            for i in range(m):
                # If the row is not empty
                if grid[i]:
                    # Find the maximum value in the current row
                    curr_pop = max(grid[i])
                    # Remove the maximum value from the current row
                    grid[i].remove(curr_pop)
                    # Update the maximum value for this iteration
                    max_row = max(max_row, curr_pop)
            # Add the maximum value of this iteration to the answer
            ans += max_row

        # Return the accumulated answer
        return ans


# Test case
grid = [
    [1, 2, 4],
    [3, 3, 1],
    [5, 6, 2]
]

# Create an instance of Solution and test the method
solution = Solution()
output = solution.deleteGreatestValue(grid)
print(output)  # Expected: 15 (6+5+4)

print(Solution.deleteGreatestValue(grid=[[1, 2, 4], [3, 3, 1]]))
