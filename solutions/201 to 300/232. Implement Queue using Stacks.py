from __future__ import annotations

from typing import Any


class MyQueue:
    def __init__(self):
        # Initialize two stacks for simulating the queue
        self.stack_main = []  # Main stack for storing elements
        self.stack_aux = []  # Auxiliary stack for temporary operations

    def push(self, x: int) -> None:
        """
        Push an element to the rear of the queue. Enqueue
        Time complexity: O(n).
        """
        # Move all elements from the main stack to the auxiliary stack
        while self.stack_main:
            self.stack_aux.append(self.stack_main.pop())

        # Add the new element to the bottom of the auxiliary stack
        self.stack_aux.append(x)

        # Move all elements back from the auxiliary stack to the main stack
        while self.stack_aux:
            self.stack_main.append(self.stack_aux.pop())

    def pop(self) -> Any | None:
        """
        Remove and return the element from the front of the queue. Dequeue
        Time complexity: O(1).
        """
        if not self.empty():
            # Pop the top element from the main stack
            return self.stack_main.pop()
        else:
            print("Queue is empty.")
            return None

    def peek(self) -> Any | None:
        """
        Return the element at the front of the queue without removing it.
        Time complexity: O(1).
        """
        if not self.empty():
            return self.stack_main[-1]
        else:
            print("Queue is empty.")
            return None

    def empty(self) -> bool:
        """
        Check if the queue is empty.
        Time complexity: O(1).
        """
        return len(self.stack_main) == 0


# Example usage:
queue = MyQueue()
queue.push(1)
queue.push(2)
queue.push(3)
print("Front of the queue:", queue.peek())  # Output: Front of the queue: 1
print("Dequeued:", queue.pop())  # Output: Dequeued: 1
print("Front of the queue:", queue.peek())  # Output: Front of the queue: 2
