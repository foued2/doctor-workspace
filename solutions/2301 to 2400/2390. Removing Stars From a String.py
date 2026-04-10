class Solution:
    @staticmethod
    def removeStars(s: str) -> str:
        # Initialize an empty stack to keep track of characters
        stack = []

        # Iterate through each character in the input string
        for c in s:
            if c == '*':
                # If the character is '*', remove the last character from the stack
                if stack:
                    stack.pop()
            else:
                # If the character is not '*', add it to the stack
                stack.append(c)

        # Join the remaining characters in the stack to form the resultant string
        return ''.join(stack)


if __name__ == '__main__':
    # Example usage: removes stars and corresponding characters from the string
    print(Solution.removeStars(s="leet**cod*e"))  # Output: "lecoe"