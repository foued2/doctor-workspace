from typing import List


class Solution:
    @staticmethod
    def isConsecutive(nums: List[int]) -> bool:
        # Converts the maximum-minimum difference into an inclusive count of elements
        # expected in a consecutive sequence.
        return max(nums) - min(nums) + 1 == len(nums)


if __name__ == '__main__':
    print(Solution.isConsecutive([1,3]))