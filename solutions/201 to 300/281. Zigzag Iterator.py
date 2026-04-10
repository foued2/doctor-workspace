class ZigzagIteratorK:
    # int[0] is index of vector of vectors list, int[1] is start of a vector, int[2] is end
    q = []
    # No map needed, directly use 'vectors' as instance variable
    vectors = []

    def __init__(self, vectors):
        self.vectors = vectors
        # Initialize the queue with information for each vector
        for i in range(len(vectors)):
            self.q.append([i, 0, len(vectors[i])])

    def next(self):
        # Get the front element from the queue
        current = self.q.pop(0)

        # Extract index, start, and end from the current element
        i = current[0]
        start = current[1]
        end = current[2]

        # Check if there are more elements in the current vector
        if start + 1 < end:
            # If there are, re-add the vector back to the queue with updated start index
            self.q.append([i, start + 1, end])

        # Return the current element from the vector
        return self.vectors[i][start]

    def hasNext(self):
        # Check if there are any elements left in the queue
        return len(self.q) != 0