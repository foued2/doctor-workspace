from typing import List


class Solution:
    @staticmethod
    def addSpaces(s: str, spaces: List[int]) -> str:
        # Initialize an empty list to store the resulting parts of the string
        res = []

        # Get the length of the string
        n = len(s)

        # Append the length of the string to the spaces list to handle the final segment of the string
        spaces.append(n)

        # Initialize pointers for iterating over the string and spaces list
        i = 0  # Pointer for the current position in the string
        j = 0  # Pointer for the current position in the spaces' list

        # Loop until we have processed the entire string
        while i < n:
            # Append the substring from the current position to the next space index
            res.append(s[i:spaces[j]])

            # Update the current position to the next space index
            i = spaces[j]

            # Move to the next index in the spaces' list
            j += 1

        # Join the list of string parts with a space and return the resulting string
        return ' '.join(res)


print(Solution.addSpaces(s="LeetcodeHelpsMeLearn", spaces=[8, 13, 15]))
