class Solution:
    def checkString(s: str) -> bool:
        # Convert the input string to a list of characters
        char_list = []
        for char in s:
            char_list.append(char)

        # Sort the list of characters
        sorted_chars = sorted(char_list)

        # Check if the sorted list is equal to the original list
        # If they are equal, the string is already sorted in ascending order
        if sorted_chars == char_list:
            return True
        else:
            return False


print(Solution.checkString(s="abab"))
