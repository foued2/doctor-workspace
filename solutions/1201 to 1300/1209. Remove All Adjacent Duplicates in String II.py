class Solution:
    @staticmethod  # This decorator indicates that the method does not require a class instance
    def removeDuplicates(s: str, k: int) -> str:
        """
        Stack Solution
        """
        # Get the length of the input string
        n = len(s)

        # Initialize a stack to keep track of characters and their counts
        stack = []

        # Iterate through each character in the string
        for i in range(n):
            # If the stack is not empty and the last character in the stack is the same as the current character
            if stack and stack[-1][0] == s[i]:
                # Increment the count of the last character in the stack
                stack[-1][1] += 1
                # If the count becomes equal to k, remove the last character from the stack
                if stack[-1][1] == k:
                    stack.pop()
            else:
                # If the stack is empty or the last character in the stack is different from the current character,
                # add the current character and a count of 1 to the stack
                stack.append([s[i], 1])

        # Reconstruct the string from the stack by repeating each character according to its count
        return "".join([i[0] * i[1] for i in stack])


if __name__ == "__main__":
    # Test the method with the given example
    print(Solution.removeDuplicates(s="deeedbbcccbdaa", k=3))