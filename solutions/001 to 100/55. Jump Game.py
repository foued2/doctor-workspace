from typing import List


class Solution:
    @staticmethod
    def canJump(nums: List[int]) -> bool:
        # If the list contains only one element, return True since it's always possible to reach the end.
        if len(nums) == 1:
            return True

        # Initialize the goal to the last index of the array.
        goal = len(nums) - 1

        # Initialize a list 'dp' to keep track of the farthest reachable index from each position.
        # Initialize the last element of 'dp' as the goal index.
        dp = [0] * (len(nums) - 1) + [goal]

        # Iterate backward from the second last index to the first index.
        for i in range(len(nums) - 2, -1, -1):
            # Check if the remaining steps needed to reach the goal from the current position 'i'
            # is less than or equal to the maximum number of steps that can be taken from 'i' (nums[i]).
            if goal - i >= nums[i]:
                # If it's possible to reach the goal from 'i', update 'dp[i]' to the value of 'nums[i]'
                # and set the new goal to 'i' since it's now the new farthest reachable index.
                dp[i] = nums[i]
                goal = i

        # If the first element of 'dp' is non-zero, it means we can reach the end.
        print(dp, len(set(dp)))
        return dp[0] != 0


print(Solution.canJump([2, 3, 1, 1, 4]))
