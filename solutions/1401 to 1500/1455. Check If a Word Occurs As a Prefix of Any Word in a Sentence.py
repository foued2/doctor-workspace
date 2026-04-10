class Solution:
    @staticmethod
    def isPrefixOfWord(sentence: str, searchWord: str) -> int:
        # Split the sentence into words
        words = sentence.split()

        # Iterate over the words with an index
        for index, word in enumerate(words):
            # Check if the searchWord is a prefix of the current word
            if word.startswith(searchWord):
                # Return the 1-based index
                return index + 1

        # If no prefix match is found, return -1
        return -1


# Example usage
if __name__ == '__main__':
    print(Solution.isPrefixOfWord("i love eating burger", "burg"))  # Output: 4
    print(Solution.isPrefixOfWord("this problem is an easy problem", "pro"))  # Output: 2