class Solution:
    @staticmethod
    def maxPower(s: str) -> int:
        ans = 1  # Initialize the maximum power to 1 (minimum value)
        count = 1  # Initialize a counter for consecutive occurrences of the same character

        # Iterate through each character in the string starting from the second character
        for i in range(1, len(s)):
            # Check if the current character is the same as the previous character
            if s[i] == s[i - 1]:
                count += 1  # If so, increment the counter
            else:
                count = 1  # If not, reset the counter to 1 (new consecutive sequence)

            # Update the maximum power with the maximum value between the current power and the counter
            ans = max(ans, count)

        # Return the maximum consecutive occurrences of the same character
        return ans


if __name__ == '__main__':
    print(Solution.maxPower(s="abbcccddddeeeeedcba"))
