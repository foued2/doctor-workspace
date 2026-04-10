from typing import List


class Solution:
    @staticmethod
    def intersection(nums1: List[int], nums2: List[int]) -> List[int]:
        # Convert lists to sets and perform set intersection
        intersection_set = set(nums1) & set(nums2)

        # Convert the result set back to a list
        return list(intersection_set)


print(Solution.intersection(nums1=[4, 9, 5], nums2=[9, 4, 9, 8, 4]))
