class Solution:
    @staticmethod
    def possibleStringCount(word: str) -> int:
        # Get the length of the input word
        n = len(word)

        # Initialize the result counter
        res = 0

        # Iterate over each character in the word except the last one
        for i in range(n - 1):
            # Check if current character is equal to the next one
            if word[i + 1] == word[i]:
                # Increment the result counter if they are equal
                res += 1

        # Return the total count, adding 1 to account for the starting string
        return res + 1


if __name__ == "__main__":
    # Example usage: count sequences in the word "abc"
    print(Solution().possibleStringCount("abc"))