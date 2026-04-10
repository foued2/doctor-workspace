class Solution:
    @staticmethod
    def repeatedCharacter(s: str) -> str:
        # Create an empty dictionary to store the count of each character
        table = {}

        # Iterate through each character in the string
        for letter in s:
            # Increment the count of the current character in the dictionary
            table[letter] = table.get(letter, 0) + 1

            # If the count of the current character reaches 2, it is the first repeated character
            if table[letter] == 2:
                return letter


if __name__ == '__main__':
    print(Solution.repeatedCharacter("abccbaacz"))

