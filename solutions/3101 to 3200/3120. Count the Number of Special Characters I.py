class Solution:
    @staticmethod
    def numberOfSpecialChars(word: str) -> int:
        # Initialize sets to store unique lowercase letters and lowercase versions of uppercase letters
        lowercase_letters = set()
        lowercase_of_uppercase_letters = set()

        # Initialize the counter for special characters
        special_char_count = 0

        # Iterate through each character in the word
        for char in word:
            # Check if the character is lowercase
            if char.islower():
                # Add the lowercase character to the set
                lowercase_letters.add(char)
            else:
                # Convert the uppercase character to lowercase and add it to the set
                lowercase_of_uppercase_letters.add(char.lower())

        # Check for intersection between the two sets
        for char in lowercase_of_uppercase_letters:
            # If the character from the uppercase set is in the lowercase set, it is special
            if char in lowercase_letters:
                special_char_count += 1

        # Return the count of special characters
        return special_char_count


print(Solution.numberOfSpecialChars(word="aaAbcBC"))
