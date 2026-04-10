class Solution:
    @staticmethod
    def isLongPressedName(name: str, typed: str) -> bool:
        # Get the lengths of the name and typed strings
        n = len(typed)
        m = len(name)

        # If the first characters don't match, return False immediately
        if typed[0] != name[0]:
            return False

        # Initialize pointers for both name (i) and typed (j) strings
        i, j = 0, 0

        # Iterate through the typed string
        while j < n:
            # If characters match in both strings, move both pointers
            if i < m and name[i] == typed[j]:
                i += 1
                j += 1
            # If characters don't match, and it's a repetition in typed, move the typed pointer
            elif j > 0 and typed[j] == typed[j - 1]:
                j += 1
            # If there's no match, and it's not a repetition, return False
            else:
                return False

        # After the loop, check if all characters in the name have been matched
        return i == m


solution = Solution()
print(solution.isLongPressedName("alex", "aaleex"))  # Should return True
print(solution.isLongPressedName("saeed", "ssaaedd"))  # Should return False
