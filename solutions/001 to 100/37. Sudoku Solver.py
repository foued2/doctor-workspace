from typing import List


class Solution:
    @staticmethod
    def solveSudoku(board: List[List[str]]) -> List[List[str]]:
        """
        Do not return anything, modify table in-place instead.
        """

        def trio(i, j, table):
            filled_digits = set()

            # Check the row
            for col in range(len(table[0])):
                if table[i][col] != '.' and table[i][col].isdigit():
                    filled_digits.add(table[i][col])

            # Check the column
            for row in range(len(table)):
                if table[row][j] != '.' and table[row][j].isdigit():
                    filled_digits.add(table[row][j])

            # Check the box
            box_row_start, box_col_start = 3 * (i // 3), 3 * (j // 3)
            for row in range(box_row_start, box_row_start + 3):
                for col in range(box_col_start, box_col_start + 3):
                    if table[row][col] != '.' and table[row][col].isdigit():
                        filled_digits.add(table[row][col])

            # Determine the digits that the empty cell should be
            all_digits = set(str(i) for i in range(1, 10))
            possible_digits = all_digits - filled_digits

            return list(possible_digits)

        def calculate_coefficients(table):
            coefficients = {}

            for i in range(len(table)):
                for j in range(len(table[0])):
                    if table[i][j] == '.':
                        trio_result = trio(i, j, table)
                        coefficients[(i, j)] = len(trio_result)

            # Sort coefficients based on the length of the trio result
            sorted_coefficients = sorted(coefficients.items(), key=lambda x: x[1])

            return sorted_coefficients

        def solve_sudoku(table):
            # Calculate initial coefficients
            coefficients = calculate_coefficients(table)

            # Iterate through the sorted coefficients
            for (i, j), _ in coefficients:
                if table[i][j] == '.':
                    # Get possible digits for the empty cell
                    possible_digits = trio(i, j, table)

                    # Fill the cell with each possible digit and explore
                    for digit in possible_digits:
                        table[i][j] = digit

                        # Recursively try to solve the updated table
                        if solve_sudoku(table):
                            return table  # Board is solved

                        # If the current placement leads to an invalid state, undo it
                        table[i][j] = '.'

                    # If no valid digit was found, backtrack to the previous state
                    return False
            #
            # No empty cell is found, the table is solved
            return True

        return solve_sudoku(board)

    print(solveSudoku(
        [["5", "3", ".", ".", "7", ".", ".", ".", "."],
         ["6", ".", ".", "1", "9", "5", ".", ".", "."],
         [".", "9", "8", ".", ".", ".", ".", "6", "."],
         ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
         ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
         ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
         [".", "6", ".", ".", ".", ".", "2", "8", "."],
         [".", ".", ".", "4", "1", "9", ".", ".", "5"],
         [".", ".", ".", ".", "8", ".", ".", "7", "9"]]))
