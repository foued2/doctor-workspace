from typing import List


class Solution:
    @staticmethod
    def isAlienSorted(words: List[str], order: str) -> bool:
        # Get the number of words in the list
        n = len(words)

        # Define a space character to pad words of different lengths
        space = ' '

        # Add space at the beginning of the order string for padding purposes
        order = space + order

        # Create a dictionary to map each character to its position in the alien dictionary order
        counter = {}
        for char in order:
            # Assign each character its index position
            counter[char] = order.index(char)

        # Compare each pair of consecutive words in the list
        for i in range(n - 1):
            # If the next word is longer, pad the current word with spaces
            if len(words[i + 1]) > len(words[i]):
                words[i] += space * (len(words[i + 1]) - len(words[i]))
            # If the next word is shorter, pad the next word with spaces
            elif len(words[i + 1]) < len(words[i]):
                words[i + 1] += space * (len(words[i]) - len(words[i + 1]))

            # Compare characters of the two words
            j = 0
            while j < len(words[i]):
                # If the character in the next word comes before the current word in the alien order, return False
                if counter[words[i + 1][j]] < counter[words[i][j]]:
                    return False
                # If the character in the next word comes after the current word in the alien order, stop comparing
                if counter[words[i + 1][j]] > counter[words[i][j]]:
                    break
                # If characters are equal, move to the next character
                else:
                    j += 1

        # If all pairs of words are in correct order, return True
        return True


print(Solution.isAlienSorted(words=["apple", "app"], order="abcdefghijklmnopqrstuvwxyz"))
