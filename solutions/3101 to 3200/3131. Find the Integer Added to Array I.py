from typing import List


class Solution:
    @staticmethod
    def addedInteger(nums1: List[int], nums2: List[int]) -> int:
        # Sort the first list of integers
        nums1 = sorted(nums1)

        # Sort the second list of integers
        nums2 = sorted(nums2)

        # Calculate the difference between the smallest element of nums2 and nums1
        ans = nums2[0] - nums1[0]

        return ans


print(Solution.addedInteger(nums1=[2, 6, 4], nums2=[9, 7, 5]))
