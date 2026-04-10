# class Solution:
#     @staticmethod
#     def reverseWords(s: str) -> str:
#         # Split the input string 's' by whitespace and remove extra spaces
#         words = s.split()
#
#         # Reverse the list of words
#         reversed_words = words[::-1]
#
#         # Join the reversed list of words back into a string with spaces
#         return ' '.join(reversed_words)
#
#
# # Test the reverseWords function
# print(Solution.reverseWords(s="a good   example"))

class Solution:
    @staticmethod
    def reverseWords(s: str) -> str:
        # Define pointers to track word boundaries
        start = 0
        end = len(s) - 1

        # Move 'start' pointer to the beginning of the first word
        while start <= end and s[start] == ' ':
            start += 1

        # Move 'end' pointer to the end of the last word
        while end >= start and s[end] == ' ':
            end -= 1

        # Initialize a list to store reversed words
        words = []

        # Iterate through the string character by character
        while start <= end:
            # Initialize a word variable to store characters of a word
            word = ''
            # Move 'start' pointer to the beginning of the word
            while start <= end and s[start] != ' ':
                word += s[start]
                start += 1
            # Append the word to the list of words
            if word:
                words.append(word)
            # Move 'start' pointer to the next character after the word
            while start <= end and s[start] == ' ':
                start += 1

        # Join the reversed words with spaces and return
        return ' '.join(words[::-1])


# Test the reverseWords function
print(Solution.reverseWords(s="a good   example"))
