from typing import List


class Solution:
    @staticmethod
    def numberOfLines(widths: List[int], s: str) -> List[int]:
        # Dictionary to hold the width of each character
        pixels = {}
        for i in range(26):
            letter = chr(ord('a') + i)
            # Add the width for each letter from 'a' to 'z'
            pixels[letter] = widths[i]

        # Variables to track the current line width and the number of lines used
        line_width = 0
        lines = 1

        # Iterate through each character in the string s
        for char in s:
            # Width of the current character
            char_width = pixels[char]
            # Check if adding this character exceeds the line width limit
            if line_width + char_width > 100:
                # Start a new line if it exceeds the limit
                lines += 1
                line_width = char_width
            else:
                # Otherwise, add the character to the current line
                line_width += char_width

        # Return the number of lines and the width used on the last line
        return [lines, line_width]


# Example usage:
widths = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
s = "abcdefghijklmnopqrstuvwxyz"
print(Solution.numberOfLines(widths, s))  # Output: [3, 60]

print(Solution.numberOfLines(
    widths=[4, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
    s="bbbcccdddaaa"))
