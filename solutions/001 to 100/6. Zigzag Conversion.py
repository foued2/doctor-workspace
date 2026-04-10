class Solution:
    @staticmethod
    def convert(s: str, numRows: int) -> str:
        if numRows == 1 or numRows >= len(s):
            return s

        # Create rows to store characters in zigzag pattern
        rows = [''] * numRows

        # In the case of a forward-backward loop, the step should be a dependent changing variable
        index, step = 0, 1

        # Traverse through each character in the string
        for char in s:
            rows[index] += char
            if index == 0:  # If we reach the first row, change direction
                step = 1
            elif index == numRows - 1:  # If we reach the last row, change direction
                step = -1
            index += step  # Move to the next row based on the direction

        # Combine rows to form the zigzag pattern
        zigzag = ''.join(rows)
        return zigzag


# Test the convert method
print(Solution.convert(s="PAYPALISHIRING", numRows=3))
