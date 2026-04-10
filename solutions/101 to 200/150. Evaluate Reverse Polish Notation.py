from typing import List


class Solution:
    @staticmethod
    def evalRPN(tokens: List[str]) -> int:
        # Initialize an empty stack to store operands
        stack = []

        # Iterate through each token in the list of tokens
        for token in tokens:
            # Check if the token represents a numeric value (positive or negative)
            if token.lstrip('-').isdigit():
                # If the token is numeric, convert it to an integer and push it onto the stack
                stack.append(int(token))
            else:
                # If the token is an operator, pop the last two operands from the stack
                num2 = stack.pop()
                num1 = stack.pop()

                # Perform the arithmetic operation based on the operator token
                if token == '+':
                    stack.append(num1 + num2)  # Addition
                elif token == '-':
                    stack.append(num1 - num2)  # Subtraction
                elif token == '*':
                    stack.append(num1 * num2)  # Multiplication
                elif token == '/':
                    # Handle division by zero
                    if num2 == 0:
                        stack.append(0)
                    else:
                        stack.append(int(num1 / num2))  # Division

        # After processing all tokens, the final result is the last value remaining on the stack
        return stack.pop()


if __name__ == '__main__':
    # Example usage: Evaluate the given RPN expression and print the result
    print(Solution.evalRPN(tokens=["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]))
