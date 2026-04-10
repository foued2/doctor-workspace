from collections import deque


class MovingAverage:
    def __init__(self, size: int):
        # Initialize the MovingAverage object with the given window size
        self.queue = deque()
        # Initialize a deque to store the elements in the window
        self.size = size
        # Initialize the current average
        self.avg = 0

    def next(self, val: int) -> float:
        # If the queue is not full, add the new value to the queue
        # and calculate the average using the sum of elements in the queue
        if len(self.queue) < self.size:
            self.queue.append(val)
            self.avg = sum(self.queue) / len(self.queue)
            return self.avg
        else:
            # If the queue is full, remove the leftmost element from the queue,
            # add the new value to the queue, and update the average
            head = self.queue.popleft()  # Remove the leftmost element
            self.queue.append(val)  # Add the new value to the queue
            # Update the average by subtracting the contribution of the removed element
            # and adding the contribution of the new element
            minus = head / self.size
            add = val / self.size
            self.avg = self.avg + add - minus
            return self.avg
