class Solution:
    @staticmethod
    def countHomogenous(s: str) -> int:
        """
        Dynamic Programming solution
        """
        # Get the length of the input string
        n = len(s)

        # Initialize the dp array where dp[i] represents the count of homogenous substrings ending at index i
        dp = [1] * n

        # Iterate through the string starting from the second character
        for i in range(1, n):
            # If the current character is the same as the previous one
            if s[i] == s[i - 1]:
                # Increment dp[i] by dp[i-1] because we can extend the homogenous substring ending at i-1 to include s[i]
                dp[i] += dp[i - 1]
            else:
                # If characters are different, reset dp[i] to 1 as it represents a new homogenous substring of length 1
                dp[i] = 1

        # Return the sum of all values in the dp array modulo (10^9 + 7) to keep the number manageable
        return sum(dp) % (10 ** 9 + 7)


# Example use case
if __name__ == "__main__":
    # Printing the result of the countHomogenous function for the input string "abbcccaa"
    print(Solution().countHomogenous("abbcccaa"))