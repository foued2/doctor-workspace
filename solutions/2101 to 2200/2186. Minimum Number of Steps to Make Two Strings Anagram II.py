class Solution:
    @staticmethod
    def minSteps(s: str, t: str) -> int:
        # Initialize the variable to count the steps required
        steps = 0

        # Create a set of unique characters from both strings
        unique_chars = set(s + t)

        # Iterate over each unique character
        for char in unique_chars:
            # Calculate the absolute difference in the count of the current character in both strings
            count_difference = abs(s.count(char) - t.count(char))
            # Add the difference to the total steps
            steps += count_difference

        # Return the total steps required to make the two strings anagrams
        return steps


# Example usage
solution = Solution()
print(solution.minSteps("friend", "family"))  # Expected output: 6
