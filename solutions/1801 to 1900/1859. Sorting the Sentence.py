class Solution:
    @staticmethod
    def sortSentence(s: str) -> str:
        # Split the input string into a list of words
        s = s.split()

        # Get the number of words in the list
        n = len(s)

        # Sort the list of words based on the last character of each word (which is a digit)
        s = sorted(s, key=lambda x: x[-1])

        # Print the sorted list of words (for debugging purposes)
        print(s)

        # Iterate through the sorted list of words
        for i in range(n):
            # Remove the last character (digit) from each word
            s[i] = s[i][:-1]

        # Join the modified words back into a single string with spaces in between
        return ' '.join(s)


print(Solution.sortSentence(s="Myself2 Me1 I4 and3"))
