from collections import defaultdict
from typing import List


class Solution:
    @staticmethod
    def tictactoe(moves: List[List[int]]) -> str:
        ans = 'Draw'
        n = len(moves)
        table_X = defaultdict(list)
        table_Y = defaultdict(list)
        if n < 9 and ans == '':
            return 'Pending'
        elif n == 9 and ans == '':
            

            return 'Draw'
        else:
            return ans


print(Solution.tictactoe(moves=[[0, 0], [2, 0], [1, 1], [2, 1], [2, 2]]))
