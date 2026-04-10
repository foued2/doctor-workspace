class MyHashMap:
    def __init__(self):
        # Initialize the hash map as a list of lists
        self.hash_map = [[] for _ in range(10000)]

    def put(self, key: int, value: int) -> None:
        # Get the index for the key
        index = key % 10000
        # Iterate through each pair in the hash map
        for pair in self.hash_map[index]:
            # If the key already exists, update its value
            if pair[0] == key:
                pair[1] = value
                return
        # If the key doesn't exist, append a new pair
        self.hash_map[index].append([key, value])

    def get(self, key: int) -> int:
        # Get the index for the key
        index = key % 10000
        # Iterate through each pair in the hash map at the calculated index
        for pair in self.hash_map[index]:
            # If the key is found, return its corresponding value
            if pair[0] == key:
                return pair[1]
        # If the key is not found, return -1 (not found)
        return -1

    def remove(self, key: int) -> None:
        # Get the index for the key
        index = key % 10000
        # Iterate through each pair in the hash map at the calculated index
        for pair in self.hash_map[index]:
            # If the key is found, remove the pair from the hash map
            if pair[0] == key:
                self.hash_map[index].remove(pair)
                return


if __name__ == '__main__':
    # Create an instance of MyHashMap
    myHashMap = MyHashMap()
    # Add key-value pairs to the hash map
    myHashMap.put(1, 1)
    myHashMap.put(2, 2)
    # Get the value corresponding to key 1 and print it
    print(myHashMap.get(1))
    # Get the value corresponding to key 3 (which doesn't exist) and print it
    print(myHashMap.get(3))
    # Update the value for key 2
    myHashMap.put(2, 1)
    # Get the updated value for key 2 and print it
    print(myHashMap.get(2))
    # Remove the key 2 from the hash map
    myHashMap.remove(2)
    # Get the value for key 2 (which has been removed) and print it
    print(myHashMap.get(2))
