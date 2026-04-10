from typing import List


class Solution:
    @staticmethod
    def findOcurrences(text: str, first: str, second: str) -> List[str]:
        # Initialize an empty list to store the resulting words
        res = []

        # Split the input text into a list of words
        text = text.split()

        # Get the total number of words in the text
        n = len(text)

        # Loop through the text, stopping 2 words before the end to avoid out-of-bounds errors
        for i in range(n - 2):
            # Check if the current word matches the 'first' word and the next word matches the 'second' word
            if text[i] == first and text[i + 1] == second:
                # If both words match, add the word following 'second' to the result list
                res.append(text[i + 2])

        # Return the list of resulting words
        return res


print(Solution.findOcurrences(text="alice is a good girl she is a good student", first="a", second="good"))
