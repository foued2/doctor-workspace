class Solution:
    @staticmethod
    def minAddToMakeValid(s: str) -> int:
        """
        Stack
        """
        # Stack to keep track of unmatched parentheses
        unmatched_stack = []

        # Iterate over each character in the input string 's'
        for char in s:
            if char == '(':
                # If the character is an opening parenthesis, push it onto the stack
                unmatched_stack.append(char)
            else:  # char == ')'
                if unmatched_stack and unmatched_stack[-1] == '(':
                    # If the stack is not empty and the top of the stack is an opening parenthesis,
                    # we have a matching pair, so pop the opening parenthesis from the stack
                    unmatched_stack.pop()
                else:
                    # If there is no matching opening parenthesis, push the closing parenthesis onto the stack
                    unmatched_stack.append(char)

        # The length of the stack represents the number of unmatched parentheses
        # which is the minimum number of insertions needed to make the string valid
        return len(unmatched_stack)


print(Solution.minAddToMakeValid(s="()))(("))
