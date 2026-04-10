from collections import Counter


class Solution:
    @staticmethod
    def minSteps(s: str, t: str) -> int:
        # Initialize the answer to store the number of steps needed
        ans = 0
        # Create a counter for all characters in string s
        counter_s = Counter(s)

        # Iterate over each character in string t
        for char in t:
            # If the character is in counter_s and has a positive count
            if char in counter_s and counter_s[char] > 0:
                # Decrement the count of the character in counter_s
                counter_s[char] -= 1

        # Iterate over the values in counter_s
        for value in counter_s.values():
            # If there are any remaining characters with a positive count
            if value > 0:
                # Add the count to the answer (each represents an extra step needed)
                ans += value

        # Return the total number of steps needed
        return ans


print(Solution.minSteps(s="leetcode", t="practice"))
