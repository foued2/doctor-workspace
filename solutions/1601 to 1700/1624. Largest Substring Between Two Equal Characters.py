class Solution:
    @staticmethod
    def maxLengthBetweenEqualCharacters(s: str) -> int:
        # Initialize a dictionary to store the first occurrence index of each character
        first_occurrence = {}

        # Initialize the maximum length as -1, assuming no valid substring is found
        max_length = -1

        # Iterate over each character in the string along with its index
        for i, char in enumerate(s):
            if char in first_occurrence:
                # Calculate the length between the current and the first occurrence of the character
                current_length = i - first_occurrence[char] - 1
                # Update the maximum length if the current length is greater
                max_length = max(max_length, current_length)
            else:
                # Store the first occurrence index of the character
                first_occurrence[char] = i

        return max_length


print(Solution.maxLengthBetweenEqualCharacters(s="scayofdzca"))
