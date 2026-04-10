class Solution:
    @staticmethod
    def longestContinuousSubstring(s: str) -> int:
        # Initialize the result variable and pointers
        res = right = 1  # res stores the length of the longest continuous substring found so far
        # right is the right pointer, indicating the end of the current substring
        left = 0  # left is the left pointer, indicating the start of the current substring

        # Define the English alphabet
        alphabet = "abcdefghijklmnopqrstuvwxyz"

        # Iterate until both pointers are within the bounds of the alphabet string
        while left < right < len(alphabet):
            # Check if the substring from alphabet
            # et[left: right+1] is present in the given string s
            if alphabet[left:right + 1] in s:
                # If the substring is present, update the result if necessary and move the right pointer
                res = max(res, right - left + 1)
                right += 1
            else:
                # If the substring is not present, move both pointers to the next position
                left += 1
                right = left + 1

        # Return the length of the longest continuous substring found
        return res


print(Solution.longestContinuousSubstring('z'))
