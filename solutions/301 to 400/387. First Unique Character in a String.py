class Solution:
    @staticmethod
    def firstUniqChar(s: str) -> int:
        """
        Queue-Hashed Table-based approach to find the index of the first non-repeating character in a string.
        """
        # Create a dictionary to store the count of each character in the string
        table = {}

        # Create a queue to store characters in the order they appear for the first time
        queue = []

        # Iterate through each character in the string
        for char in s:
            # Update the count of the character in the dictionary
            if char in table:
                table[char] += 1
            else:
                table[char] = 1
                # Append the character to the queue if it's encountered for the first time
                queue.append(char)

        # Iterate through the characters in the queue
        for char in queue:
            # Check if the count of the character is 1 (i.e., it's non-repeating)
            if table[char] == 1:
                # Return the index of the first occurrence of the non-repeating character in the original string
                return s.index(char)

        # If no non-repeating character is found, return -1
        return -1


if __name__ == '__main__':
    # Test the function with a sample string
    print(Solution.firstUniqChar("aabb"))  # Output: -1 (No non-repeating characters)
