from typing import List


class Solution:
    @staticmethod
    def luckyNumbers(matrix: List[List[int]]) -> List[int]:
        # Initialize the list to store lucky numbers
        lucky = []

        # Iterate through each row in the matrix
        for row in matrix:
            # Find the minimum value in the current row
            candidate = min(row)
            # Find the column index of the minimum value in the current row
            col = row.index(candidate)

            # Assume the candidate is the maximum in its column
            isMaximum = True
            # Check if the candidate is the maximum in its column
            for rowcol in matrix:
                if rowcol[col] > candidate:
                    # If any value in the column is greater, the candidate is not a lucky number
                    isMaximum = False
                    break

            # If the candidate is the maximum in its column, it is a lucky number
            if isMaximum:
                lucky.append(candidate)

        # Return the list of lucky numbers
        return lucky


# Example usage
matrix = [
    [3, 7, 8],
    [9, 11, 13],
    [15, 16, 17]
]
print(Solution().luckyNumbers(matrix))  # Expected output: [15]

