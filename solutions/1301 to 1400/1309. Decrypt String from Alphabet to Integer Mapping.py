class Solution:
    @staticmethod
    def freqAlphabets(s: str) -> str:
        # Create a dictionary to map digits to corresponding letters
        alphabet = {}

        # Add mappings for digits '2' to '9' to their corresponding letters 'b' to 'i'
        for i in range(1, 10):
            alphabet[str(i)] = chr(ord('a') + i - 1)

        # Add mappings for two-digit numbers followed by '#' ('10#' to '26#') to their corresponding letters 'j' to 'z'
        for i in range(10, 27):
            alphabet[str(i) + '#'] = chr(ord('a') + i - 1)

        # Convert the keys of the dictionary to a list to perform slicing
        keys = list(alphabet.keys())

        # Replace the patterns with '#' first to avoid conflicts with single-digit replacements
        for key in keys[9:]:
            if key in s:
                # Replace the pattern in the string s with its corresponding letter
                s = s.replace(key, alphabet[key])

        # Replace single-digit patterns
        for key in keys[:9]:
            if key in s:
                # Replace the pattern in the string s with its corresponding letter
                s = s.replace(key, alphabet[key])

        # Return the decoded string
        return s


print(Solution.freqAlphabets(s="10#11#12"))


class Solution:
    @staticmethod
    def freqAlphabets(s: str) -> str:
        # Initialize an empty list to store parts of the decoded string
        res = []
        # Start from the end of the string
        i = len(s) - 1

        # Iterate backward through the string
        while i >= 0:
            if s[i] == '#':
                # If the current character is '#', it means the current letter is encoded as a two-digit number
                # Append the substring representing the two-digit number to the result list
                res.append(s[i - 2:i])
                # Move the index three steps back to skip the processed part
                i -= 3
            else:
                # If the current character is not '#', it represents a single-digit number
                # Append this single character to the result list
                res.append(s[i])
                # Move the index one step back
                i -= 1

        # Reverse the result list to correct the order
        # Convert each numeric string in the result list to its corresponding letter
        # Use chr() to convert the number to the appropriate letter
        # The lambda function converts each numeric string to a character
        # int(s) converts the string to an integer
        # ord('a') - 1 adjusts the conversion to the correct alphabet index
        # Join the list of characters into a final decoded string
        return ''.join(map(lambda s: chr(int(s) + ord('a') - 1), res[::-1]))
