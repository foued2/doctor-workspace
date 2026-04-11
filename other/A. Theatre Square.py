import math


class Solution:
    @staticmethod
    def theatreSquare(n: int, m: int, a: int) -> int:
        """
        :param n: length of theatre square
        :param m: width of theatre square
        :param a: side of flagstone
        :return: minimum number of flagstones
        """
        return math.ceil(n / a) * math.ceil(m / a)


length, width, side = map(int, input().rstrip().split())
sol = Solution()
print(sol.theatreSquare(length, width, side))
