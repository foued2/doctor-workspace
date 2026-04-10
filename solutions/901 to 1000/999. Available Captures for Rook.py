from typing import List


class Solution:
    @staticmethod
    def numRookCaptures(board: List[List[str]]) -> int:
        # Initialize the answer to 0, which will store the number of pawns the rook can capture
        ans = 0

        # List to store positions of all pieces on the board
        pieces = []

        # List to store the position of the rook
        rook = []

        # Traverse the board to find all pieces and the rook's position
        for i in range(8):
            for j in range(8):
                # If the cell is not empty, add the position of the piece to the list
                if board[i][j] != '.':
                    pieces.append([i, j])

                # If the cell contains the rook, store the rook's position
                if board[i][j] == 'R':
                    rook.extend([i, j])

        # Find the index of the rook in the pieces' list
        idx = pieces.index(rook)

        # Initialize a set to store the positions of neighboring pieces
        neighbors = set()

        # Add the positions of the pieces to the left and right of the rook if they exist
        if 0 <= idx - 1 < len(pieces):
            neighbors.add(tuple(pieces[idx - 1]))  # Add the left neighbor
        if 0 <= idx + 1 < len(pieces):
            neighbors.add(tuple(pieces[idx + 1]))  # Add the right neighbor

        # Sort the pieces by column to check vertical neighbors
        pieces = sorted(pieces, key=lambda x: x[1])

        # Update the index of the rook after sorting
        idx = pieces.index(rook)

        # Add the positions of the pieces above and below the rook if they exist
        if 0 <= idx - 1 < len(pieces):
            neighbors.add(tuple(pieces[idx - 1]))  # Add the above neighbor
        if 0 <= idx + 1 < len(pieces):
            neighbors.add(tuple(pieces[idx + 1]))  # Add the below neighbor

        # Check each neighboring piece to see if it is a pawn that can be captured
        for cell in neighbors:
            if cell[0] == rook[0] or cell[1] == rook[1]:
                if board[cell[0]][cell[1]] == 'p':
                    ans += 1  # Increment the answer if a pawn is found

        # Return the total number of pawns the rook can capture
        return ans


print(Solution.numRookCaptures(
    board=[[".", ".", ".", ".", ".", ".", ".", "."],
           ["p", ".", ".", "p", ".", ".", ".", "p"],
           ["p", "p", ".", ".", ".", ".", "p", "p"],
           ["p", "p", "p", ".", "R", "p", "p", "p"],
           ["p", "p", ".", ".", ".", ".", "p", "p"],
           ["p", ".", ".", "p", ".", ".", ".", "p"],
           [".", ".", ".", ".", ".", ".", ".", "."],
           [".", ".", ".", ".", ".", ".", ".", "."]]))
