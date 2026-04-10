class Solution:
    @staticmethod
    def isCircularSentence(sentence: str) -> bool:
        # Split the sentence into individual words
        words = sentence.split(' ')

        # Check if the first character of the first word matches the last character of the last word
        if words[0][0] != words[-1][-1]:
            return False

        # Iterate over the words to check the condition for adjacent words
        for i in range(len(words) - 1):
            # Check if the last character of the current word matches the first character of the next word
            if words[i][-1] != words[i + 1][0]:
                return False

        # If all conditions are satisfied, return True
        return True


# Example usage:
sentence = "hello on no oh"
result = Solution.isCircularSentence(sentence)
print(result)  # Output should be True

sentence = "hello oh no"
result = Solution.isCircularSentence(sentence)
print(result)  # Output should be False
