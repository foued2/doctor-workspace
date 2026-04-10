class Solution:
    @staticmethod
    def minLength(s: str) -> int:
        # Convert string to list for easy manipulation
        s = list(s)
        # Length of the list
        n = len(s)
        # Initial index
        i = 0

        # Iterate over the list
        while i < n - 1:
            if s[i] == 'A' and s[i + 1] == 'B':
                # Remove 'A' and 'B'
                s.pop(i + 1)
                s.pop(i)
                # Update the length
                n -= 2
                # Move index back to check for overlapping patterns
                i = max(0, i - 1)
            elif s[i] == 'C' and s[i + 1] == 'D':
                # Remove 'C' and 'D'
                s.pop(i + 1)
                s.pop(i)
                # Update the length
                n -= 2
                # Move index back to check for overlapping patterns
                i = max(0, i - 1)
            else:
                # Move to the next index
                i += 1

        # The remaining length of the list is the result
        return len(s)


print(Solution.minLength(s="ABFCACDB"))


class Solution:
    @staticmethod
    def minLength(s: str) -> int:
        """Stack approach.
        TC O(n) - one pass over an array.
        SC O(n) - memory for stack of all characters of s in the worst case.
        """
        stack = []

        # Iterate through each character in the string
        for char in s:
            # If the current character is 'B' and the stack's top is 'A', pop the stack
            if char == 'B':
                if stack and stack[-1] == 'A':
                    stack.pop()
                else:
                    stack.append(char)
            # If the current character is 'D' and the stack's top is 'C', pop the stack
            elif char == 'D':
                if stack and stack[-1] == 'C':
                    stack.pop()
                else:
                    stack.append(char)
            else:
                # If the current character does not form a pair, push it onto the stack
                stack.append(char)

        # The length of the stack represents the length of the string after all valid pairs are removed
        return len(stack)


# Example usage
s = "ABFCACDB"
solution = Solution()
result = solution.minLength(s)
print(result)  # Output: 2 (remaining characters are "FC")
