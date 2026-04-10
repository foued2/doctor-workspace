from typing import List


class Solution:
    @staticmethod
    def findIntersectionValues(nums1: List[int], nums2: List[int]) -> List[int]:
        # Find the set of common elements between nums1 and nums2
        overlap = set(nums1) & set(nums2)
        # Initialize counters for the number of occurrences of common elements in nums1 and nums2
        n1 = n2 = 0
        # Iterate over each element in nums1
        for n in nums1:
            # If the current element is in the set of common elements, increment n1
            if n in overlap:
                n1 += 1
        # Iterate over each element in nums2
        for n in nums2:
            # If the current element is in the set of common elements, increment n2
            if n in overlap:
                n2 += 1
        # Return a list containing the counts of occurrences of common elements in nums1 and nums2
        return [n1, n2]


print(Solution.findIntersectionValues(nums1=[3, 4, 2, 3], nums2=[1, 5]))
