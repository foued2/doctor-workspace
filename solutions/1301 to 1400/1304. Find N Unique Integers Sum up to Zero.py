from typing import List


class Solution:
    @staticmethod
    def sumZero(n: int) -> List[int]:
        # Check if 'n' is even
        if n % 2 == 0:
            # If even, generate a list of consecutive negative and positive integers
            res = [i for i in range(-(n // 2), 0)] + [i for i in range(1, (n // 2) + 1)]
        else:
            # If odd, generate a list of consecutive integers including zero
            res = [i for i in range(-(n // 2), (n // 2) + 1)]

        # Return the generated list
        return res


print(Solution.sumZero(n=6))
