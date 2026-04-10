class Solution:
    @staticmethod
    def capitalizeTitle(title: str) -> str:
        # Initialize an empty list to store the processed words
        res = []

        # Split the input title string into individual words
        title = title.split()

        # Iterate through each word in the list
        for word in title:
            # Convert the word to lowercase
            word = word.lower()

            # If the word length is greater than 2, capitalize the first letter
            if len(word) > 2:
                word = word.capitalize()

            # Add the processed word to the result list
            res.append(word)

        # Join the words in the result list with a space and return the final string
        return ' '.join(res)


# Example usage:
title = "this is a test title"
print(Solution.capitalizeTitle(title))  # Output should be "This is a Test Title"

print(Solution.capitalizeTitle(title="First leTTeR of EACH Word"))
