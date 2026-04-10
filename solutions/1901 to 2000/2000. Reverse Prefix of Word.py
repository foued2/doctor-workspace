class Solution:
    @staticmethod
    def reversePrefix(word: str, ch: str) -> str:
        # Check if the character 'ch' is present in the word
        if ch in word:
            # Find the index of the first occurrence of 'ch' in the word
            idx = word.index(ch)
            # Reverse the prefix of the word up to the index of 'ch' (inclusive)
            reversed_prefix = word[:idx + 1][::-1]
            # Concatenate the reversed prefix with the remaining part of the word
            return reversed_prefix + word[idx + 1:]
        # If 'ch' is not found in the word, return the word as it is
        return word


print(Solution.reversePrefix(word="acked", ch="d"))
