class TrieNode:
    # Define a class to represent a node in the trie.
    def __init__(self):
        # Initialize a TrieNode object.
        self.children = {}  # A dictionary to store child nodes
        self.is_end_of_word = False  # Indicates if the node represents the end of a word


class Trie:
    # Define a class to represent a trie data structure.
    def __init__(self):
        # Initialize a Trie object with a root node.
        self.root = TrieNode()  # Initialize the root node of the trie

    def insert(self, word):
        # Insert a word into the trie.
        current = self.root  # Start from the root node
        for char in word:
            # Traverse through each character in the word
            if char not in current.children:
                # If the character is not present in the children of the current node
                current.children[char] = TrieNode()  # Create a new node for the character
            current = current.children[char]  # Move to the next node
        current.is_end_of_word = True  # Mark the end of the word

    def search(self, word):
        # Search for a word in the trie.
        current = self.root  # Start from the root node
        for char in word:
            # Traverse through each character in the word
            if char not in current.children:
                # If any character is not present, the word is not in the trie
                return False
            current = current.children[char]  # Move to the next node
        return current.is_end_of_word  # Return True if the end of the word is reached

    def startsWith(self, prefix):
        # Check if the trie contains a word with a given prefix.
        current = self.root  # Start from the root node
        for char in prefix:
            # Traverse through each character in the prefix
            if char not in current.children:
                # If any character is not present, the prefix is not in the trie
                return False
            current = current.children[char]  # Move to the next node
        return True  # Return True if all characters of the prefix are found in the trie


# Usage example:
trie = Trie()
trie.insert("apple")
print(trie.search("apple"))  # Output: True
print(trie.search("app"))  # Output: False
print(trie.startsWith("app"))  # Output: True
trie.insert("app")
print(trie.search("app"))  # Output: True
