class Solution:
    @staticmethod
    def climbStairs(n: int) -> int:
        # Base cases: if n is 1, 2, or 3, the result is n itself
        if n <= 3:
            return n

        # Initialize a dynamic programming list with base cases
        dp = [1, 2, 3] + [0 for _ in range(n - 3)]

        # Iterate from 3 to n (exclusive) to fill the dp list
        for i in range(3, n):
            # The number of ways to reach the ith step is the sum of ways to reach (i-1)th and (i-2)th steps
            dp[i] = dp[i - 1] + dp[i - 2]

        # Return the result which is the number of ways to reach the nth step
        return dp[n - 1]


# Test the climbStairs method with an input of 6 steps
print(Solution.climbStairs(6))
