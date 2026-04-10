class Solution:
    @staticmethod
    def areOccurrencesEqual(s: str) -> bool:
        # Dictionary to store the frequency of each character
        frequency_table = {}

        # Iterate over each character in the string 's'
        for char in s:
            # Increment the count for the character 'char' in the frequency table
            frequency_table[char] = frequency_table.get(char, 0) + 1

        # Convert the values of the frequency table (character counts) to a set
        unique_frequencies = set(frequency_table.values())

        # If the set has only one unique value, it means all characters have the same frequency
        return len(unique_frequencies) == 1


print(Solution.areOccurrencesEqual(s="aaabb"))
