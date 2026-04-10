class Solution:
    @staticmethod
    def maxRepeating(sequence: str, word: str) -> int:
        """
        Dynamic Programming, String Matching
        """
        # Lengths of the sequence and word.
        n = len(sequence)
        m = len(word)

        # Initialize a DP table to store the maximum repetitions at each index.
        dp = [0] * (n + 1)

        # Iterate through each index of the sequence.
        for i in range(1, n + 1):
            # Check if the current position in the sequence matches the end of the word.
            if sequence[i - 1:i - 1 + m] == word:
                # If so, update the DP table with the maximum repetition at this index.
                dp[i] = dp[i - m] + 1

        # Return the maximum repetition found in the DP table.
        return max(dp)


if __name__ == '__main__':
    print(Solution.maxRepeating("aaabaaaabaaabaaaabaaaabaaaabaaaaba", "aaaba"))
    print(Solution.maxRepeating(sequence="ababc", word="ab"))
    print(Solution.maxRepeating(sequence="ababc", word="ba"))
    print(Solution.maxRepeating(sequence="ababc", word="ac"))
    print(Solution.maxRepeating(sequence="aaa", word="a"))
