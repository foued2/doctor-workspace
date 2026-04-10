from typing import List


class Solution:
    @staticmethod
    def mostWordsFound(sentences: List[str]) -> int:
        # Initialize a variable to keep track of the maximum number of words found
        max_words = 0

        # Iterate through each sentence in the list of sentences
        for i in range(len(sentences)):
            # Split the sentence into words using the space character as the delimiter
            words = sentences[i].split(' ')

            # Calculate the number of words in the current sentence
            num_words = len(words)

            # Update the maximum number of words found if the current sentence has more words
            if num_words > max_words:
                max_words = num_words

        # Return the maximum number of words found in any sentence
        return max_words


# Example usage:
sentences = [
    "This is the first sentence",
    "Here is another sentence with more words",
    "Short sentence",
    "This one is the longest sentence in the list so far"
]
print(Solution.mostWordsFound(sentences))  # Output: 9

print(Solution.mostWordsFound(
    sentences=["alice and bob love leetcode", "i think so too", "this is great thanks very much"]))
