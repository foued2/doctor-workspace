class Solution:
    @staticmethod
    def minimizedStringLength(s: str) -> int:
        # Convert the string 's' to a set to eliminate duplicate characters.
        unique_characters = set(s)

        # Return the number of unique characters by measuring the length of the set.
        return len(unique_characters)


print(Solution.minimizedStringLength(s="data"))
