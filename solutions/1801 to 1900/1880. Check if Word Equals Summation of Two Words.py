class Solution:
    @staticmethod
    def isSumEqual(firstWord: str, secondWord: str, targetWord: str) -> bool:
        # Function to convert a word into its numerical representation
        def word_to_num(word):
            # Initialize the result
            res = 0
            # Get the length of the word
            n = len(word)
            # Iterate through each character in the word
            for i in range(n):
                # Shift the digits to the left
                res *= 10
                # Convert the character to its numerical value and add to the result
                res += ord(word[i]) - ord('a')
            # Return the numerical representation
            return res

        # Check if the sum of the numerical representations of the first two words is equal to the numerical
        # representation of the target word
        return word_to_num(firstWord) + word_to_num(secondWord) == word_to_num(targetWord)


print(Solution.isSumEqual(firstWord="aaa", secondWord="a", targetWord="aaaa"))
