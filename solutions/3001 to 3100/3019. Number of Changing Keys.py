class Solution:
    @staticmethod
    def countKeyChanges(s: str) -> int:
        # Get the length of the input string
        n = len(s)
        # Initialize a counter for the number of key changes
        count = 0
        # Iterate over the characters of the string up to the second-to-last character
        for i in range(n - 1):
            # Check if the current character and the next character are different (ignoring case)
            if s[i + 1] != s[i].lower() and s[i + 1] != s[i].upper():
                # If they are different, increment the counter for key changes
                count += 1
        # Return the total count of key changes
        return count


print(Solution.countKeyChanges(s="aAbBcC"))
