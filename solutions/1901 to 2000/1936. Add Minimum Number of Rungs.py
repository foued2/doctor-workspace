from typing import List


class Solution:
    @staticmethod
    def addRungs(rungs: List[int], dist: int) -> int:
        # Initialize the answer to count the number of additional rungs needed
        ans = 0

        # Add a ground level rung at height 0 to the beginning of the rungs' list
        rungs = [0] + rungs

        # Get the number of rungs, including the added ground level rung
        n = len(rungs)

        # Iterate over the rungs starting from the second element (index 1)
        for i in range(1, n):
            # Calculate the height difference between the current rung and the previous rung
            height = rungs[i] - rungs[i - 1]

            # If the height difference is greater than the allowed distance
            if height > dist:
                # Calculate the number of additional rungs needed to fill the gap
                # We use (height - 1) // dist because we need to add enough rungs
                # to ensure each segment between rungs is at most 'dist' apart
                ans += (height - 1) // dist

        # Return the total number of additional rungs needed
        return ans


# Example usage:
rungs = [1, 3, 7]
dist = 2
solution = Solution()
print(solution.addRungs(rungs, dist))  # Output: 2

print(Solution.addRungs(rungs=[3, 7, 8, 10], dist=3))
