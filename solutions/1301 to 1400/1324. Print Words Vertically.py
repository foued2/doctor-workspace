from typing import List


class Solution:
    @staticmethod
    def printVertically(s: str) -> List[str]:
        # Initialize the result list
        res = []

        # Split the input string into words
        s = s.split()

        # Determine the maximum length of the words
        m = 0
        for word in s:
            m = max(m, len(word))

        # Loop through each character position up to the maximum word length
        for i in range(m):
            vertical = ''  # Initialize the vertical slice for this position

            # Loop through each word to collect the characters at the current position
            for word in s:
                if len(word) > i:
                    vertical += word[i]  # Append the character if the word is long enough
                else:
                    vertical += ' '  # Append a space if the word is too short

            # Right strip to remove trailing spaces and append to the result list
            res.append(vertical.rstrip())

        return res  # Return the list of vertical slices


print(Solution.printVertically(s="TO BE OR NOT TO BE"))
