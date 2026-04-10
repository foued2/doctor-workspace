class Solution:
    @staticmethod
    def removeDuplicates(s: str) -> str:
        # Initialize an empty list to use as a stack
        stack = []
        # Iterate over each character in the input string
        for char in s:
            # Check if the stack is not empty and the top element is the same as the current character
            if stack and stack[-1] == char:
                # If the top element of the stack is the same as the current character, pop the stack
                stack.pop()
            else:
                # Otherwise, push the current character onto the stack
                stack.append(char)
        # Join the elements of the stack into a single string to form the result
        ans = ''.join(stack)
        # Return the resulting string
        return ans


# Example usage
print(Solution.removeDuplicates(s="azxxzy"))  # Output: "ay"
