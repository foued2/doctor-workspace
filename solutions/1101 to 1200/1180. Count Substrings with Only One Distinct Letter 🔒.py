class Solution:
    @staticmethod
    def countLetters(s: str) -> int:
        # Initialize the answer to zero.
        ans = 0
        # Get the length of the input string.
        n = len(s)
        # Initialize the index for traversing the string.
        i = 0

        # Loop through the string until the end is reached.
        while i < n:
            # Initialize the streak length of consecutive identical characters.
            streak = 1

            # Check for consecutive identical characters.
            while i + 1 < n and s[i] == s[i + 1]:
                # Increase the streak length.
                streak += 1
                # Move to the next character in the string.
                i += 1

            # Calculate the number of substrings that can be formed from the current streak.
            # This is the sum of the first 'streak' natural numbers.
            ans += (streak * (streak + 1)) // 2
            # Move to the next character in the string.
            i += 1

        # Return the total number of substrings.
        return ans


print(Solution.countLetters(s="aaaaaaaaaa"))
