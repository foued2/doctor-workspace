from typing import List

class Solution:
    @staticmethod
    def vowelStrings(words: List[str], left: int, right: int) -> int:
        # Define the list of vowels
        vowels = ['a', 'e', 'i', 'o', 'u']
        # Initialize a count variable to keep track of the number of words that start and end with a vowel
        count = 0
        # Iterate through the words in the specified range [left, right]
        for i in range(left, right + 1):
            # Check if the first and last characters of the current word are vowels
            if words[i][0] in vowels and words[i][-1] in vowels:
                # If both are vowels, increment the count
                count += 1
        # Return the final count of words that start and end with a vowel
        return count


print(Solution.vowelStrings(words=["hey", "aeo", "mu", "ooo", "artro"], left=1, right=4))
