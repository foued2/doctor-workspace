from typing import List


class Solution:
    @staticmethod
    def countBits(n: int) -> List[int]:
        dp = [0 for _ in range(n + 1)]
        for i in range(n + 1):
            # m = bin(i)[2:]
            # bit = int(m, 2)
            # dp[i] |= 1 << bit
            dp[i] = bin(i).count('1')
        return dp

    print(countBits(2))
