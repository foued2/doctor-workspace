class Array:
    def __init__(self, capacity):
        """
        Initialize an Array object with a given capacity.
        """
        self.capacity = capacity  # Maximum capacity of the array
        self.size = 0  # Current size of the array
        self.data = [None] * capacity  # Initialize the array with None values

    def get(self, index):
        """
        Get the element at the specified index in the array.
        """
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")  # Handle index out of bounds
        return self.data[index]  # Return the element at the specified index

    def set(self, index, value):
        """
        Set the value at the specified index in the array.
        """
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")  # Handle index out of bounds
        self.data[index] = value  # Set the value at the specified index

    def append(self, value):
        """
        Append a value to the end of the array.
        """
        if self.size >= self.capacity:
            raise OverflowError("Array is full")  # Handle array full
        self.data[self.size] = value  # Add the value to the end of the array
        self.size += 1  # Increment the size of the array

    def remove(self, index):
        """
        Remove the element at the specified index from the array.
        """
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")  # Handle index out of bounds
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]  # Shift elements to the left
        self.data[self.size - 1] = None  # Set the last element to None
        self.size -= 1  # Decrement the size of the array


# Usage example:
arr = Array(5)  # Create an array with capacity 5
arr.append(10)
arr.append(20)
arr.append(30)
print(arr.get(1))  # Output: 20
arr.set(1, 25)
print(arr.get(1))  # Output: 25
arr.remove(0)
print(arr.get(0))  # Output: 20
