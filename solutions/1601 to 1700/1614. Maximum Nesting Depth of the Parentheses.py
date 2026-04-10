class Solution:
    @staticmethod
    def maxDepth(s: str) -> int:
        """
        Stack
        """
        # Initialize an empty stack to keep track of opening parentheses
        stack = []

        # Initialize a variable to keep track of the maximum nesting depth encountered
        max_depth = 0

        # Iterate through each character in the input string
        for char in s:
            # If the character is an opening parenthesis
            if char == '(':
                # Push it onto the stack
                stack.append(char)

                # Update the max_depth if the current stack size is greater than the current max_depth
                max_depth = max(max_depth, len(stack))

            # If the character is a closing parenthesis
            elif char == ')':
                # Pop an element from the stack
                stack.pop()

        # Return the maximum nesting depth encountered
        return max_depth


print(Solution.maxDepth(s="(1+(2*3)+((8)/4))+1"))
print(Solution.maxDepth(s="(1)+((2))+(((3)))"))
