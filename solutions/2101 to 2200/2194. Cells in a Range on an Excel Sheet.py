from typing import List


class Solution:
    @staticmethod
    def cellsInRange(s: str) -> List[str]:
        # Split the input string into start and end parts
        start, end = s.split(':')

        # Get the starting and ending column letters and row numbers
        start_col = ord(start[0])  # ASCII value of the starting column letter
        end_col = ord(end[0])  # ASCII value of the ending column letter
        start_row = int(start[1])  # Starting row number
        end_row = int(end[1])  # Ending row number

        # Initialize the result list to store the cell labels
        result = []

        # Iterate over the range of column letters
        for col in range(start_col, end_col + 1):
            # Iterate over the range of row numbers
            for row in range(start_row, end_row + 1):
                # Create the cell label by combining the column letter and row number
                cell_label = chr(col) + str(row)
                # Add the cell label to the result list
                result.append(cell_label)

        # Return the list of cell labels
        return result


# Example usage
solution = Solution()
print(solution.cellsInRange("A1:C3"))  # Expected output: ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
print(solution.cellsInRange("B2:D4"))  # Expected output: ['B2', 'B3', 'B4', 'C2', 'C3', 'C4', 'D2', 'D3', 'D4']
