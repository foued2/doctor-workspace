from typing import List


class Solution:
    @staticmethod
    def jump(nums: List[int]) -> int:
        n = len(nums)
        if n == 1:
            return 0

        jumps = 0
        farthest = 0
        current_end = 0

        # Iterate through the array till the second last index
        for i in range(n - 1):
            # Update the furthest reachable index considering the current jump
            next_jump = i + nums[i]
            if next_jump > farthest:
                farthest = next_jump

            # If the current index equals the current boundary,
            # it means we need to jump to reach farther indices
            if i == current_end:
                # Update the boundary to the furthest reachable index for the next jump
                current_end = farthest
                # Increment the number of jumps
                jumps += 1

                # Check if we've reached the end of the array
                if current_end >= n - 1:
                    break

        return jumps


# Test the solution with the given example
print(Solution.jump([2, 3, 0, 1, 4]))
