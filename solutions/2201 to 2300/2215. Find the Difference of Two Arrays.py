from typing import List


class Solution:
    @staticmethod
    def findDifference(nums1: List[int], nums2: List[int]) -> List[List[int]]:
        # Convert both lists to sets to remove duplicates and for faster operations
        set1, set2 = set(nums1), set(nums2)

        # Find elements in nums1 that are not in nums2
        unique_to_nums1 = list(set1 - set2)

        # Find elements in nums2 that are not in nums1
        unique_to_nums2 = list(set2 - set1)

        # Return the result as a list of two lists
        return [unique_to_nums1, unique_to_nums2]


# Test cases
print(Solution.findDifference([1, 2, 3], [2, 4, 6]))  # Expected output: [[1, 3], [4, 6]]
print(Solution.findDifference([1, 2, 2, 1], [2, 2]))  # Expected output: [[1], []]
print(Solution.findDifference([4, 3, 3], [5, 4, 4, 3]))  # Expected output: [[], [5]]
