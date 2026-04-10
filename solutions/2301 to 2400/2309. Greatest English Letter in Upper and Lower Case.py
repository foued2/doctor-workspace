class Solution:
    @staticmethod
    def greatestLetter(s: str) -> str:
        """
        Enumeration, Alphabet order
        """
        # Convert the input string 's' to a set of unique characters for quick lookup
        s = set(s)

        # ASCII values for 'Z' and 'z'
        upper_Z = ord('Z')
        lower_z = ord('z')

        # Iterate over the range of 26 letters in the alphabet
        for i in range(26):
            # Calculate the current uppercase and lowercase letters to check
            uppercase_letter = chr(upper_Z - i)
            lowercase_letter = chr(lower_z - i)

            # Check if both the current uppercase and lowercase letters are in the set 's'
            if uppercase_letter in s and lowercase_letter in s:
                # If both are found, return the uppercase letter
                return uppercase_letter

        # If no such letter is found, return an empty string
        return ''


print(Solution.greatestLetter(s="lEeTcOdE"))
