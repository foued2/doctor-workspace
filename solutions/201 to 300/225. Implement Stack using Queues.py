from collections import deque


class MyStack:

    def __init__(self):
        self.queue1 = deque()
        self.queue2 = deque()

    def push(self, x: int) -> None:
        # Push the new element onto queue1
        self.queue1.append(x)

    def pop(self) -> int:
        # Move all elements except the last one from queue1 to queue2
        while len(self.queue1) > 1:
            self.queue2.append(self.queue1.popleft())
        # Retrieve the last element from queue1 (top element of the stack)
        top_element = self.queue1.popleft()
        # Swap the names of queue1 and queue2
        self.queue1, self.queue2 = self.queue2, self.queue1
        return top_element

    def top(self) -> int:
        # Similar to pop, but don't remove the element from queue1
        while len(self.queue1) > 1:
            self.queue2.append(self.queue1.popleft())
        top_element = self.queue1.popleft()
        self.queue2.append(top_element)
        self.queue1, self.queue2 = self.queue2, self.queue1
        return top_element

    def empty(self) -> bool:
        # The stack is empty if both queues are empty
        return not self.queue1 and not self.queue2
