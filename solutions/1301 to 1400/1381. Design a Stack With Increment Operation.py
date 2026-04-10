class CustomStack:

    def __init__(self, maxSize: int):
        """
        Stack, Design
        """
        # Initialize an empty list to act as the stack
        self.stack = []
        # Set the maximum size of the stack
        self.maxsize = maxSize

    def push(self, x: int) -> None:
        # Check if the stack has not reached its maximum size
        if len(self.stack) < self.maxsize:
            # Append the element to the stack if there's space
            self.stack.append(x)
        # If the stack is full, do nothing
        else:
            pass

    def pop(self) -> int:
        # Check if the stack is not empty
        if self.stack:
            # Pop the top element from the stack and return it
            return self.stack.pop()
        else:
            # If the stack is empty, return -1
            return -1

    def increment(self, k: int, val: int) -> None:
        # Calculate the range to which the increment should be applied
        # It should be the minimum of k and the current stack size
        limit = min(k, len(self.stack))
        # Increment the first 'limit' elements by 'val'
        for i in range(limit):
            self.stack[i] += val


# Example usage:
cs = CustomStack(3)
cs.push(1)
cs.push(2)
cs.increment(2, 100)
print(cs.pop())  # Output: 102
print(cs.pop())  # Output: 101
print(cs.pop())  # Output: -1
