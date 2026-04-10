from typing import List


class Solution:
    @staticmethod
    def uniqueMorseRepresentations(words: List[str]) -> int:
        # List of Morse code representations for each letter from 'a' to 'z'
        morse = [".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---", "-.-", ".-..", "--", "-.",
                 "---", ".--.", "--.-", ".-.", "...", "-", "..-", "...-", ".--", "-..-", "-.--", "--.."]

        # Dictionary to map each letter from 'a' to 'z' to its corresponding Morse code
        encode = {}
        for i in range(26):
            # Map each letter to its Morse code representation
            encode[chr(ord('a') + i)] = morse[i]

        # Set to store unique Morse code transformations of the words
        res = set()

        # Iterate through each word in the input list
        for word in words:
            # Initialize an empty string to build the Morse code transformation of the word
            decode = ''
            # Convert each character in the word to its Morse code and concatenate to 'decode'
            for char in word:
                decode += encode[char]
            # Add the complete Morse code transformation of the word to the set
            res.add(decode)

        # The number of unique Morse code transformations is the size of the set 'res'
        ans = len(res)

        # Return the number of unique Morse code transformations
        return ans


print(Solution.uniqueMorseRepresentations(words=["a"]))
