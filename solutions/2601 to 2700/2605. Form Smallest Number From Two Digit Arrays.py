from typing import List


class Solution:
    @staticmethod
    def minNumber(nums1: List[int], nums2: List[int]) -> int:
        # Find the intersection of nums1 and nums2
        inter = set(nums1).intersection(nums2)

        # If there is at least one common element
        if len(inter) >= 1:
            # Return the smallest common element
            return min(inter)
        else:
            # Find the smallest element in nums1
            m1 = min(nums1)
            # Find the smallest element in nums2
            m2 = min(nums2)

            # Form the smallest two-digit number possible by combining m1 and m2,
            # This can be achieved by taking the smaller element as the tens' digit
            # and the larger element as the units' digit
            return min(m1, m2) * 10 + max(m1, m2)


# Example usage
nums1 = [3, 5, 9]
nums2 = [1, 7, 3]
print(Solution().minNumber(nums1, nums2))  # Output should be 3 (common element)

nums1 = [4, 6, 8]
nums2 = [1, 2, 9]
print(Solution().minNumber(nums1, nums2))  # Output should be 14 (the smallest formed number)
