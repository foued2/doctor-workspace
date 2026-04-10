from typing import List


class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        """
        Backtracking, Matrix
        """
        if not board or not board[0] or not word:
            return False

        rows = len(board)
        cols = len(board[0])
        word_len = len(word)

        def dfs(r: int, c: int, i: int) -> bool:
            if i == word_len:
                return True
            if r < 0 or r >= rows or c < 0 or c >= cols:
                return False
            if board[r][c] != word[i]:
                return False

            # Mark visited in-place and backtrack after exploring neighbors.
            tmp = board[r][c]
            board[r][c] = "#"

            found = (
                dfs(r + 1, c, i + 1)
                or dfs(r - 1, c, i + 1)
                or dfs(r, c + 1, i + 1)
                or dfs(r, c - 1, i + 1)
            )

            board[r][c] = tmp
            return found

        for r in range(rows):
            for c in range(cols):
                if dfs(r, c, 0):
                    return True

        return False
