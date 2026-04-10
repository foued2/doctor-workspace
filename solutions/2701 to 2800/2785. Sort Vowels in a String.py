class Solution:
    @staticmethod
    def sortVowels(s: str) -> str:
        # Define a string containing all the vowels in both uppercase and lowercase
        VOWELS = 'AEIOUaeiou'

        # Create a translation table that maps each vowel to an underscore ('_')
        # str.maketrans takes two arguments of equal length and creates a mapping
        # between characters in the first argument to characters in the second argument
        TRANS = str.maketrans(VOWELS, '_' * len(VOWELS))
        # Translate all vowels in the input string 's' to underscores
        s2 = s.translate(TRANS)
        print(s2)

        # Iterate over each vowel in the VOWELS string
        for vowel in VOWELS:
            # Replace underscores in 's2' with the current vowel, for the number
            # of times the vowel appears in the original string 's'
            s2 = s2.replace('_', vowel, s.count(vowel))

        # Return the transformed string 's2' where all vowels have been sorted
        return s2


# Example usage:
sol = Solution()
print(sol.sortVowels("Hello, World!"))


class Solution:
    @staticmethod
    def sortVowels(s: str) -> str:
        # Set of vowels (both lowercase and uppercase) for quick lookup
        vowels_set = {"a", "e", "i", "o", "u", "A", "E", "I", "O", "U"}

        # Convert the input string 's' to a list of characters
        char_list = list(s)

        # List to store all vowels found in the input string 's'
        vowels_list = []

        # Iterate over each character in the list 'char_list' by index
        for i in range(len(char_list)):
            # If the current character is a vowel
            if char_list[i] in vowels_set:
                # Append the vowel to the 'vowels_list'
                vowels_list.append(char_list[i])
                # Replace the vowel in the list 'char_list' with an asterisk ('*')
                char_list[i] = "*"

        # Sort the list of vowels
        vowels_list.sort()

        # Initialize a variable to track the index of the sorted vowels
        sorted_vowel_index = 0

        # Iterate over each character in the list 'char_list' by index again
        for i in range(len(char_list)):
            # If the current character is an asterisk ('*')
            if char_list[i] == "*":
                # Replace the asterisk with the next vowel from the sorted 'vowels_list'
                char_list[i] = vowels_list[sorted_vowel_index]
                # Increment the index to move to the next vowel
                sorted_vowel_index += 1

        # Join the list of characters back into a single string and return it
        return "".join(char_list)


# Example usage:
sol = Solution()
print(sol.sortVowels("Hello, World!"))
