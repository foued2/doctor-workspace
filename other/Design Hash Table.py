class HashTable:
    def __init__(self, size=100):
        """
        Initialize the hash table with a specified size.

        Args:
        - size: The size of the hash table (default is 100).
        """
        self.size = size
        self.table = [[] for _ in range(size)]  # Initialize the table as a list of empty lists

    def _hash(self, key):
        """
        Compute the hash value for a given key.

        Args:
        - key: The key for which to compute the hash value.

        Returns:
        - The hash value for the given key.
        """
        return hash(key) % self.size  # Use Python's built-in hash function to compute the hash value

    def put(self, key, value):
        """
        Insert a key-value pair into the hash table.

        Args:
        - key: The key associated with the value.
        - value: The value to be inserted.
        """
        index = self._hash(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:  # If the key already exists, update the value
                self.table[index][i] = (key, value)
                return
        self.table[index].append((key, value))  # Append the key-value pair to the appropriate bucket

    def get(self, key):
        """
        Retrieve the value associated with a given key from the hash table.

        Args:
        - key: The key for which to retrieve the value.

        Returns:
        - The value associated with the given key, or None if the key is not found.
        """
        index = self._hash(key)
        for k, v in self.table[index]:
            if k == key:
                return v  # Return the value associated with the key
        return None  # Return None if the key is not found

    def remove(self, key):
        """
        Remove a key-value pair from the hash table.

        Args:
        - key: The key to be removed.
        """
        index = self._hash(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                del self.table[index][i]  # Remove the key-value pair if the key is found
                return


# Create a hash table with default size (100)
hash_table = HashTable()

# Insert key-value pairs into the hash table
hash_table.put("apple", 5)  # Insert key "apple" with value 5
hash_table.put("banana", 7)  # Insert key "banana" with value 7
hash_table.put("orange", 3)  # Insert key "orange" with value 3

# Retrieve values from the hash table
print(hash_table.get("apple"))   # Output: 5
print(hash_table.get("banana"))  # Output: 7
print(hash_table.get("grape"))   # Output: None (Key not found)

# Update a key-value pair in the hash table
hash_table.put("apple", 10)  # Update value for key "apple" to 10
print(hash_table.get("apple"))  # Output: 10

# Remove a key-value pair from the hash table
hash_table.remove("banana")  # Remove key-value pair for key "banana"
print(hash_table.get("banana"))  # Output: None (Key not found)
