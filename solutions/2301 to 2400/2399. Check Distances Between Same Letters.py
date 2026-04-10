from typing import List


class Solution:
    @staticmethod
    def checkDistances(s: str, distance: List[int]) -> bool:
        # Iterate over the indices of the distance list (0 to 25, for each letter a to z)
        for index in range(len(distance)):
            # Calculate the character corresponding to the current index
            char = chr(index + ord('a'))

            # If the character is not in the string 's', continue to the next iteration
            if char not in s:
                continue

            # Find the first occurrence index of the character in the string 's'
            first_occurrence_index = s.index(char)

            # Calculate the expected second occurrence index based on the distance list
            expected_second_occurrence_index = first_occurrence_index + distance[index] + 1

            # If the expected second occurrence index is out of bounds, return False
            if expected_second_occurrence_index >= len(s):
                return False

            # Check if the character at the expected second occurrence index matches the current character
            if s[expected_second_occurrence_index] != char:
                return False

        # If all characters satisfy the condition, return True
        return True


print(Solution.checkDistances(s="cc",
                              distance=[1, 3, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
