class Solution:
    @staticmethod
    def isSubstringPresent(s: str) -> bool:
        # Iterate over the indices of the string up to the second-to-last character
        for i in range(len(s) - 1):
            # Extract the substring of length 2 starting at index i
            substring = s[i:i + 2]
            # Check if the current substring exists in the string except for the characters at indices i and i+1
            if substring in s[::-1]:
                # If the substring is found, return True
                return True
        # If no such substring is found, return False
        return False


print(Solution.isSubstringPresent("abcd"))
