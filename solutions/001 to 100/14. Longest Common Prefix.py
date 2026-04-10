# from typing import List
#
#
# class TrieNode:
#     # Define a class to represent a node in the trie.
#     def __init__(self):
#         # Initialize a TrieNode object.
#         self.children = {}  # Dictionary to store child nodes
#         self.is_end_of_word = False  # Indicates if the node represents the end of a word
#
#
# class Trie:
#     # Define a class to represent a trie data structure.
#     def __init__(self):
#         # Initialize a Trie object with a root node.
#         self.root = TrieNode()  # Initialize the root node of the trie
#
#     def insert(self, word):
#         # Insert a word into the trie.
#         current = self.root  # Start from the root node
#         for char in word:
#             # Traverse through each character in the word
#             if char not in current.children:
#                 # If the character is not present in the children of the current node
#                 current.children[char] = TrieNode()  # Create a new node for the character
#             current = current.children[char]  # Move to the next node
#         current.is_end_of_word = True  # Mark the end of the word
#
#     def longestCommonPrefix(self):
#         # Find the longest common prefix in the trie.
#         current = self.root  # Start from the root node
#         prefix = ''  # Initialize the prefix string
#         while current and len(current.children) == 1 and not current.is_end_of_word:
#             # Iterate while there is only one child node and it's not the end of a word
#             char = next(iter(current.children))  # Get the only child node's character
#             prefix += char  # Append the character to the prefix
#             current = current.children[char]  # Move to the next node
#         return prefix  # Return the longest common prefix found
#
#
# class Solution:
#     # Define a class to encapsulate the solution methods.
#     @staticmethod
#     def longestCommonPrefix(strs: List[str]) -> str:
#         # Find the longest common prefix among a list of strings using a trie.
#         if not strs:
#             return ''  # Return an empty string if the list is empty
#         trie = Trie()  # Create a new trie object
#         for word in strs:
#             trie.insert(word)  # Insert each word from the input list into the trie
#         return trie.longestCommonPrefix()  # Find the longest common prefix using the trie
#
#
# # Example usage:
# print(Solution().longestCommonPrefix(["flower", "flow", "flight"]))  # Output: "fl"


from typing import List


class Solution:
    @staticmethod
    def longestCommonPrefix(strs: List[str]) -> str:
        if not strs:
            return ""

        prefix = ""
        for i, char in enumerate(strs[0]):
            for word in strs[1:]:
                if i >= len(word) or word[i] != char:
                    return prefix
            prefix += char
        return prefix


# Example usage:
solution = Solution()
print(solution.longestCommonPrefix(["flower", "flow", "flight"]))  # Output: "fl"

# from typing import List
#
#
# class Solution:
#     @staticmethod
#     def longestCommonPrefix(strs: List[str]) -> str:
#         if not strs:
#             return ""
#
#         # Sort the list of strings to ensure that the shortest string comes first
#         strs.sort()
#
#         # Compare the first and last strings in the sorted list
#         first_str = strs[0]
#         last_str = strs[-1]
#
#         # Iterate over the characters of the first string
#         for i, char in enumerate(first_str):
#             # If the character at the same index in the last string does not match, return the prefix
#             if char != last_str[i]:
#                 return first_str[:i]
#
#         # Return the first string if all characters match until the end
#         return first_str
#
#
# # Example usage:
# solution = Solution()
# print(solution.longestCommonPrefix(strs=["dog", "racecar", "car"]))  # Output: "fl"
