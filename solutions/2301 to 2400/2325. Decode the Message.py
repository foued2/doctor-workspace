class Solution:
    @staticmethod
    def decodeMessage(key: str, message: str) -> str:
        # Initialize an empty string to store the decoded message
        ans = ''

        # Create a list of all lowercase alphabet characters
        alphabet = [chr(ord('a') + i) for i in range(26)]

        # Initialize an empty dictionary to store the cipher mapping
        cypher = {}

        # Iterate over each character in the key string
        for char in key:
            # Skip spaces in the key
            if char == ' ':
                continue
            # If the character is not already in the cypher dictionary,
            # add it to the dictionary and map it to the next character in the alphabet list
            if char not in cypher:
                cypher[char] = alphabet.pop(0)

        # Iterate over each character in the message string
        for char in message:
            # If the character is a space, add a space to the decoded message
            if char == ' ':
                ans += ' '
            # If the character is in the cypher dictionary, add the corresponding
            # decoded character to the decoded message
            elif char in cypher:
                ans += cypher[char]

        # Return the fully decoded message
        return ans


print(Solution.decodeMessage(key="the quick brown fox jumps over the lazy dog", message="vkbs bs t suepuv"))
