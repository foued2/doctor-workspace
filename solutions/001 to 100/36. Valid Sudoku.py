from typing import List


class Solution:
    @staticmethod
    def isValidSudoku(board: List[List[str]]) -> bool:

        for i in range(len(board)):
            row, column = list(), list()

            for j in range(len(board)):
                row_cell, column_cell = board[i][j], board[j][i]

                if row_cell.isdigit():
                    if int(row_cell) not in row:
                        row += [int(row_cell)]
                    else:
                        return False

                if column_cell.isdigit():
                    if int(column_cell) not in column:
                        column += [int(column_cell)]
                    else:
                        return False

        box_size = 3
        step_size = 3

        for i in range(0, len(board) - box_size + 1, step_size):
            for j in range(0, len(board) - box_size + 1, step_size):

                box = list()

                for row in board[i:i + step_size]:
                    for cell in row[j:j + box_size]:

                        if cell.isdigit():
                            if int(cell) not in box:
                                box += [int(cell)]
                            else:
                                return False

        return True

    print(isValidSudoku(
        [["5", "3", ".", ".", "7", ".", ".", ".", "."],
         ["6", ".", ".", "1", "9", "5", ".", ".", "."],
         [".", "9", "8", ".", ".", ".", ".", "6", "."],
         ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
         ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
         ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
         [".", "6", ".", ".", ".", ".", "2", "8", "."],
         [".", ".", ".", "4", "1", "9", ".", ".", "5"],
         [".", ".", ".", ".", "8", ".", ".", "7", "9"]]))
