class Solution:
    @staticmethod
    def checkIfPangram(sentence: str) -> bool:
        """
        Bitmask
        """
        # Initialize a bitmask to represent the presence of letters
        bitmask = 0

        # Iterate through each letter in the sentence
        for letter in sentence:
            # Calculate the index of the letter in the bitmask (0-indexed)
            index = ord(letter) - ord('a')

            # Set the corresponding bit to 1 in the bitmask
            bitmask |= (1 << index)
            print(bin(bitmask))

        # Check if the bitmask has all bits set (representing all letters of the alphabet)
        if bitmask == (1 << 26) - 1:
            return True
        else:
            return False


print(Solution.checkIfPangram(sentence="thequickbrownfoxjumpsoverthelazydog"))
