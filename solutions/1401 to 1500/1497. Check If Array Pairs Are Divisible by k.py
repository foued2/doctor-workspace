from typing import List


class Solution:
    @staticmethod
    def canArrange(arr: List[int], k: int) -> bool:
        n = len(arr)
        for i in range(n // 2):
            if (arr[i] + arr[n - i - 1]) % k != 0:
                return False
        return True


if __name__ == '__main__':
    print(Solution.canArrange(arr=[1, 2, 3, 4, 5, 10, 6, 7, 8, 9], k=5))
    print(Solution.canArrange(arr=[1, 2, 3, 4, 5, 6], k=7))
    print(Solution.canArrange(arr=[1, 2, 3, 4, 5, 6], k=10))
