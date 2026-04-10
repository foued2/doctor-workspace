from typing import List


class Solution:
    @staticmethod
    def getCommon(nums1: List[int], nums2: List[int]) -> int:
        """
        Binary search
        """
        # Initialize the common variable to infinity to store the smallest common element
        common = float('inf')

        # Ensure nums1 is the smaller or equal length list for efficiency
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1

        # Iterate over each element in nums1
        for num in nums1:
            # Initialize pointers for binary search in nums2
            left, right = 0, len(nums2) - 1

            # Perform binary search
            while left <= right:
                mid = (left + right) // 2
                if nums2[mid] == num:
                    # If the element is found, update the common variable with the smallest value
                    common = min(num, common)
                    break
                elif nums2[mid] > num:
                    # Adjust the right pointer if mid-value is greater than the target
                    right = mid - 1
                else:
                    # Adjust the left pointer if mid-value is less than the target
                    left = mid + 1

        # Check if a common element was found and return it, else return -1
        return common if common != float('inf') else -1


# Example usage:
nums1 = [1, 2, 3, 4, 5]
nums2 = [3, 4, 5, 6, 7]
print(Solution.getCommon(nums1, nums2))  # Expected output: 3

nums1 = [1, 3, 5, 7]
nums2 = [2, 4, 6, 8]
print(Solution.getCommon(nums1, nums2))  # Expected output: -1

print(Solution.getCommon(nums1=[1, 2, 3], nums2=[2, 4]))


class Solution:
    @staticmethod
    def getCommon(nums1: List[int], nums2: List[int]) -> int:
        # Convert both lists to sets
        set1 = set(nums1)
        set2 = set(nums2)

        # Find the intersection of the two sets
        common_set = set1.intersection(set2)

        # Convert the set back to a sorted list (if needed)
        return min(common_set) if common_set else -1


# Example usage:
nums1 = [1, 2, 3, 4, 5]
nums2 = [3, 4, 5, 6, 7]
print(Solution.getCommon(nums1, nums2))  # Expected output: [3, 4, 5]

nums1 = [1, 3, 5, 7]
nums2 = [2, 4, 6, 8]
print(Solution.getCommon(nums1, nums2))  # Expected output: []
