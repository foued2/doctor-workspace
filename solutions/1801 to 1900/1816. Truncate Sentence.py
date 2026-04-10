class Solution:
    @staticmethod
    def truncateSentence(s: str, k: int) -> str:
        # Split the input string s into a list of words using whitespace as the delimiter
        words = s.split()

        # Select the first k words from the list of words
        truncated_words = words[:k]

        # Join the selected words back into a single string with spaces separating them
        result = ' '.join(truncated_words)

        # Return the resulting truncated sentence
        return result


print(Solution.truncateSentence(s="What is the solution to this problem", k=4))
