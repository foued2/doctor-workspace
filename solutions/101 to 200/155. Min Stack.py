class MinStack:
    def __init__(self):
        # Initialize an empty stack to store values along with their corresponding minimum value
        self.stack = []

    def push(self, val: int) -> None:
        # Determine the minimum value for the new element
        # If the stack is empty or the new value is smaller than the current minimum,
        # set the new minimum to the new value
        if not self.stack or val < self.getMin():
            min_val = val
        else:
            min_val = self.getMin()

        # Push the value along with the current minimum value onto the stack
        self.stack.append((val, min_val))

    def pop(self) -> None:
        # To pop an element from the stack, we simply remove the topmost element
        self.stack.pop()

    def top(self) -> int:
        # Return the value of the topmost element in the stack
        return self.stack[-1][0]

    def getMin(self) -> int:
        # Return the minimum value stored at the top of the stack
        return self.stack[-1][1]


# Example usage
if __name__ == "__main__":
    # Create a MinStack object
    min_stack = MinStack()

    # Push elements onto the stack
    min_stack.push(-2)
    min_stack.push(0)
    min_stack.push(-3)

    # Retrieve the minimum value in the stack
    print("Minimum value in the stack:", min_stack.getMin())  # Output: -3

    # Pop an element from the stack
    min_stack.pop()

    # Retrieve the top element of the stack
    print("Top element of the stack:", min_stack.top())  # Output: 0

    # Retrieve the minimum value in the stack after popping an element
    print("Minimum value in the stack after popping:", min_stack.getMin())  # Output: -2
