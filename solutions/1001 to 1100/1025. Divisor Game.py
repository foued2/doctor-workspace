class Solution:
    @staticmethod
    def divisorGame(n: int) -> bool:
        # Initialize dynamic programming table
        dp = [False] * (n + 1)
        dp[0] = False
        dp[1] = False

        # Loop through each number up to n
        for i in range(2, n + 1):
            # Assume Alice starts with the number i, try to find a divisor that leads to a win for Alice
            for j in range(1, i):
                if i % j == 0 and dp[i - j] is False:
                    # If there is a divisor j such that the next position (i - j) is a losing position for Bob,
                    # then Alice can win by choosing j
                    dp[i] = True
                    break  # Break the loop as Alice has found a winning move

        # Return the result for the given number n
        return dp[n]


if __name__ == '__main__':
    # Test cases
    print(Solution.divisorGame(n=2))  # Alice can win by choosing 1
    print(Solution.divisorGame(n=15))  # Alice can win by choosing 1 or 2

