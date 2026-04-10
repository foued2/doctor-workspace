class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            return None

    def peek(self):
        if not self.is_empty():
            return self.stack[-1]
        else:
            return None

    def is_empty(self):
        return len(self.stack) == 0

    def size(self):
        return len(self.stack)


class Solution:
    @staticmethod
    def isValid(s: str) -> bool:
        # Create an instance of the stack
        stack = Stack()
        # Define the mapping of opening and closing brackets
        bracket_map = {')': '(', '}': '{', ']': '['}

        # Iterate through each character in the string
        for char in s:
            # If the character is an opening bracket, push it onto the stack
            if char not in bracket_map:
                stack.push(char)
            # If the character is a closing bracket
            else:
                # If the stack is not empty, and the top of the stack matches the opening bracket for the current
                # closing bracket
                if stack.is_empty() or stack.pop() != bracket_map[char]:
                    return False

        # If the stack is empty, all brackets are matched
        return stack.is_empty()


# Test the solution
if __name__ == "__main__":
    solution = Solution()
    print(solution.isValid("()"))  # Output: True
    print(solution.isValid("()[]{}"))  # Output: True
    print(solution.isValid("(]"))  # Output: False
    print(solution.isValid("([)]"))  # Output: False
    print(solution.isValid("{[]}"))  # Output: True
