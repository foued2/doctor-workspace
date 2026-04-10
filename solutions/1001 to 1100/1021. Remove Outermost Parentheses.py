class Solution:
    @staticmethod
    def removeOuterParentheses(s: str) -> str:
        """
        Stack, Parentheses
        """
        # Initialize an empty list to store the result
        ans = []

        # Initialize a stack to keep track of parentheses
        stack = []

        # Iterate through each character in the string `s`
        for char in s:
            if char == '(':
                # If the stack is not empty, this '(' is not an outer parenthesis
                if stack:
                    ans.append(char)
                # Push the open parenthesis onto the stack
                stack.append(char)
            else:
                # Pop the last open parenthesis from the stack
                stack.pop()
                # If the stack is not empty after popping, this ')' is not an outer parenthesis
                if stack:
                    ans.append(char)

        # Join the list into a string and return the result
        return ''.join(ans)


print(Solution.removeOuterParentheses(s="(()())(())(()(()))"))
