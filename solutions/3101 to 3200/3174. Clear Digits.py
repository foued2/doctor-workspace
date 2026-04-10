class Solution:
    @staticmethod
    def clearDigits(s: str) -> str:
        # Initialize an empty stack to hold characters
        stack = []

        # Iterate over each character in the input string
        for char in s:
            if stack and char.isdigit():
                # If the stack is not empty and the current character is a digit,
                # pop the last character from the stack (remove the preceding character)
                stack.pop()
            else:
                # Otherwise, add the current character to the stack
                stack.append(char)

        # Join the characters in the stack to form the resulting string
        return ''.join(stack)


# Example usage
solution = Solution()
print(solution.clearDigits("abc3d2ef"))  # Output: "abcef"
print(solution.clearDigits("a1b2c3"))  # Output: ""
print(solution.clearDigits("abc"))  # Output: "abc"

print(Solution.clearDigits(s="cb34"))
