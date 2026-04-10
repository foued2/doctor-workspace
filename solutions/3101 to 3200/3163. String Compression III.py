class Solution:
    @staticmethod
    def compressedString(word: str) -> str:
        # Initialize an empty string to store the compressed result
        comp = ''

        # Get the length of the input word
        n = len(word)

        # Initialize the index i to 0 (start from the first character)
        i = 0

        # Loop through the word until the end
        while i < n:
            # Initialize count to 1 for the current character
            count = 1

            # Loop to count consecutive identical characters
            while i + 1 < n and word[i] == word[i + 1] and count < 9:
                count += 1
                i += 1

            # Append the count and the character to the compressed string
            comp += str(count) + word[i]

            # Move to the next character
            i += 1

        # Return the compressed string
        return comp


print(Solution.compressedString(word="aaaaaaaaaaaaaabb"))
