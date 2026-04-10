from typing import List


class Solution:
    @staticmethod
    def maximumValue(strs: List[str]) -> int:
        # Initialize the variable `ans` to store the maximum value found
        ans = 0

        # Iterate through each string in the input list `strs`
        for s in strs:
            # Check if the current string is composed only of digits
            if s.isdigit():
                # Convert the string to an integer
                curr = int(s)
            else:
                # If not all digits, the current value is the length of the string
                curr = len(s)

            # Update `ans` to be the maximum of its current value or the current value
            ans = max(ans, curr)

        # Return the maximum value found
        return ans


print(Solution.maximumValue(strs=["alic3", "bob", "3", "4", "00000"]))
