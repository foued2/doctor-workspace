class MyHashSet:
    def __init__(self):
        self.hash_set = set()  # Initialize an empty set to store hash set elements

    def add(self, key: int) -> None:
        self.hash_set.add(key)  # Add the specified element to the set

    def remove(self, key: int) -> None:
        if key in self.hash_set:  # Check if the element exists in the hash set
            self.hash_set.remove(key)  # Remove the element from the set if it exists

    def contains(self, key: int) -> bool:
        return key in self.hash_set  # Return True if the element is present in the set, False otherwise


if __name__ == '__main__':
    # Create an instance of MyHashSet
    myHashSet = MyHashSet()

    # Add elements to the hash set
    myHashSet.add(1)
    myHashSet.add(2)

    # Print whether specified elements exist in the hash set
    print(myHashSet.contains(1))  # Output: True
    print(myHashSet.contains(3))  # Output: False

    # Add a duplicate element to the hash set (which is ignored)
    myHashSet.add(2)

    # Print whether the duplicate element exists in the hash set
    print(myHashSet.contains(2))  # Output: True

    # Remove an element from the hash set
    myHashSet.remove(2)

    # Print whether the removed element exists in the hash set
    print(myHashSet.contains(2))  # Output: False
