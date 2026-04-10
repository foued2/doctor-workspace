class Solution:
    @staticmethod
    def mergeAlternately(word1: str, word2: str) -> str:
        # Initialize an empty string to store the merged string
        merged = ''

        # Initialize pointers for both strings
        pointer1, pointer2 = 0, 0

        # Iterate through both strings until one of them reaches its end
        while pointer1 < len(word1) and pointer2 < len(word2):
            # Append characters alternately from both strings to the merged string
            merged += word1[pointer1]
            pointer1 += 1
            merged += word2[pointer2]
            pointer2 += 1

        # If word2 is longer than word1, append the remaining characters from word2 to the merged string
        if len(word2) > len(word1):
            merged += word2[len(word1):]
        # If word1 is longer than word2, append the remaining characters from word1 to the merged string
        elif len(word2) < len(word1):
            merged += word1[len(word2):]

        # Return the merged string
        return merged


# Test the function
print(Solution.mergeAlternately(word1="ab", word2="pqrs"))

