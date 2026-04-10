from typing import List


class Solution:
    @staticmethod
    def getConcatenation(nums: List[int]) -> List[int]:
        nums.extend(nums)
        return nums

if __name__ == '__main__':
    print(Solution.getConcatenation(nums=[1, 3, 2, 1]))
