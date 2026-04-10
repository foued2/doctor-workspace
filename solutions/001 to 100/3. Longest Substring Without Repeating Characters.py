# class HashTable:
#     def __init__(self):
#         self.table = {}  # Initialize an empty dictionary as the table
#
#     def put(self, key, value):
#         self.table[key] = value  # Insert the key-value pair into the table
#
#     def get(self, key):
#         return self.table.get(key, -1)  # Retrieve the value associated with the key from the table, return -1 if not
#         # found
#
#
# def lengthOfLongestSubstring(s):
#     start = 0  # Initialize the starting index of the current substring
#     max_length = 0  # Initialize the maximum length of the substring
#
#     for i, char in enumerate(s):  # Iterate through each character and its index in the input string
#         if char_map.get(char) >= start:  # If the current character is already present in char_map and its index is
#             # greater than or equal to the current start index
#             start = char_map.get(char) + 1  # Update the start index to the next position after the last occurrence
#             # of the repeating character
#         max_length = max(max_length, i - start + 1)  # Calculate the length of the current substring and update
#         # max_length if necessary
#         char_map.put(char, i)  # Insert the character and its index into char_map
#
#     return max_length  # Return the maximum length of the longest substring without repeating characters
#
#
# char_map = HashTable()  # Create an instance of the HashTable class called char_map
# s = "pythonProject()"
# hash_table = lengthOfLongestSubstring(s)
# print("hash_table", hash_table)


class Solution:
    @staticmethod
    def lengthOfLongestSubstring(s: str) -> int:
        """
        The function calculates the length of the longest substring without repeating characters.
        :param s: This is a string.
        :return: This function returns an integer which is the length of the longest substring without
        repeating characters.
        """

        # Initialize a set to keep track of the characters currently in the sliding window
        chars = set()

        # Initialize the maximum length of the substring and the left pointer of the sliding window
        max_length = left = 0

        # Iterate over the string, with 'right' being the right pointer of the sliding window
        for right in range(len(s)):

            # If the character at the right pointer of the window already exists in the set (i.e., in the window),
            # remove the character at the left pointer from the set and move the left pointer one step to the right,
            # This effectively shrinks the window from the left until we have a window with unique characters again
            while s[right] in chars:
                chars.remove(s[left])
                left += 1

            # If the character at the right pointer is unique (it's not in the set / window),
            # add it to the set / window
            chars.add(s[right])

            # After processing the character at the right pointer, compare the length of the current window
            # (right - left + 1) with the maximum length. If it's greater, update the maximum length
            max_length = max(max_length, right - left + 1)

        # Return the maximum length of the unique-character substring after the end of the loop
        return max_length

    s = "pythonProject()"
    sliding_window = lengthOfLongestSubstring(s)
    print("sliding_window", sliding_window)
