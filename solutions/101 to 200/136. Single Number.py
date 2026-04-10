from functools import reduce
from operator import xor
from typing import List


class Solution:
    @staticmethod
    def singleNumber(nums: List[int]) -> int:
        res = set()
        for num in nums:
            if num in res:
                res.remove(num)
            else:
                res.add(num)
        return list(res)[0]
        # return reduce(xor, nums)

    print(singleNumber(nums=[4, 1, 2, 1, 2]))
