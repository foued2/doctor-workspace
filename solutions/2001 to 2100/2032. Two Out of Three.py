from typing import List


class Solution:
    @staticmethod
    def twoOutOfThree(nums1: List[int], nums2: List[int], nums3: List[int]) -> List[int]:
        # Convert lists to sets to remove duplicates and enable set operations
        set_nums1 = set(nums1)
        set_nums2 = set(nums2)
        set_nums3 = set(nums3)

        # Find intersection of set_nums1 and set_nums2
        intersection_1_2 = set_nums1.intersection(set_nums2)
        # Find intersection of set_nums2 and set_nums3
        intersection_2_3 = set_nums2.intersection(set_nums3)
        # Find intersection of set_nums1 and set_nums3
        intersection_1_3 = set_nums1.intersection(set_nums3)

        # Combine all unique elements that appear in at least two sets
        result_set = intersection_1_2.union(intersection_2_3, intersection_1_3)

        # Convert the set to a list before returning
        return list(result_set)


# Example usage:
solution = Solution()
result = solution.twoOutOfThree([1, 2, 3], [4, 2, 3], [5, 2, 3])
print(result)  # Output: [2, 3]
