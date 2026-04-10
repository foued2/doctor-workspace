class Solution:
    @staticmethod
    def maxNumberOfBalloons(text: str) -> int:
        # Initialize a dictionary to count the occurrences of each letter in the word "balloon"
        balloon = {'b': 0, 'a': 0, 'l': 0, 'o': 0, 'n': 0}

        # Iterate through each letter in the input text
        for letter in text:
            # Check if the current letter is one of the letters in the word "balloon"
            if letter in balloon:
                # If it is, increment the count of that letter in the balloon dictionary
                balloon[letter] += 1

        # Calculate the maximum number of complete "balloon" strings that can be formed,
        # The maximum number is determined by the lowest count of any letter in the word "balloon"
        min_count = min(balloon['b'], balloon['a'], balloon['l'] // 2, balloon['o'] // 2, balloon['n'])

        return min_count


print(Solution.maxNumberOfBalloons(text="leetcode"))
