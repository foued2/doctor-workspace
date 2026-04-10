class Solution:
    @staticmethod
    def findPermutationDifference(s: str, t: str) -> int:
        score = 0

        # Iterate through each character in the string s along with its index
        for index, ch in enumerate(s):
            # Find the position of the character ch in the string t
            t_index = t.find(ch)

            # Calculate the absolute difference between the current index in s and the found index in t
            difference = abs(t_index - index)

            # Add the difference to the total score
            score += difference

        # Return the final computed score
        return score


# Example usage
solution = Solution()
print(solution.findPermutationDifference("abc", "bca"))  # Expected output: 4
