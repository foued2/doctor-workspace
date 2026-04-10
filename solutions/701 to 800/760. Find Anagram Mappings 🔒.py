from typing import List
from collections import defaultdict


class Solution:
    @staticmethod
    def anagramMappings(nums1: List[int], nums2: List[int]) -> List[int]:
        """
        Hash table, Stack, O(n) time complexity
        """
        # Initialize a default dict to store the indices of elements in nums2
        mapper = defaultdict(set)
        res = []
        # Populate the default dict with indices of elements from nums2
        for i, num in enumerate(nums2):
            mapper[num].add(i)

        # Generate the list of mapped positions from nums1 to nums2
        for num in nums1:
            res.append(mapper[num].pop())

        return res


print(Solution.anagramMappings([12, 28, 46, 32, 50], [50, 12, 32, 46, 28]))
