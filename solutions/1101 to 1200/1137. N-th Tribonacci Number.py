class Solution:
    @staticmethod
    def tribonacci(n: int, memo=None) -> int:
        """
        Memoization solution for Tribonacci sequence generation.
        """
        # Base cases for the Tribonacci sequence
        if memo is None:
            memo = {}
        if n == 0:
            return 0
        if n == 1:
            return 1
        if n == 2:
            return 1

        # Check if the value for n has already been computed and stored in the memoization dictionary
        if n in memo:
            return memo[n]

        # If the value for n is not in the memoization dictionary, calculate it and store it in the dictionary
        memo[n] = Solution.tribonacci(n - 1, memo) + Solution.tribonacci(n - 2, memo) + Solution.tribonacci(n - 3, memo)

        # Return the calculated value for n
        return memo[n]


if __name__ == '__main__':
    # Test cases
    print(Solution.tribonacci(25))  # Output: 4 (Tribonacci sequence: 0, 1, 1, 2, 4)


class Solution:
    @staticmethod
    def tribonacci(n: int) -> int:
        """
        Dynamic programming
        """
        # Initialize the Tribonacci sequence with the first three terms
        dp = [0, 1, 1]

        # If n is less than 3, return the nth term from the precalculated sequence
        if n < 3:
            return dp[n]

        # Iterate from the 4th term up to the nth term
        for i in range(3, n + 1):
            # Calculate the next term in the sequence by summing the previous three terms
            next_ = sum(dp)
            # Update the dynamic programming list by shifting the values and appending the next term
            dp[0], dp[1], dp[2] = dp[1], dp[2], next_

        # Return the nth term of the Tribonacci sequence
        return dp[2]


if __name__ == '__main__':
    # Test cases
    print(Solution.tribonacci(25))  # Output: 4 (Tribonacci sequence: 0, 1, 1, 2, 4)
