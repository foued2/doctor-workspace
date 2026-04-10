from typing import List


class Solution:
    @staticmethod
    def binary_search(arr: List[int], target: int) -> int:
        # Binary search implementation
        left, right = 0, len(arr) - 1
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return -1

    @staticmethod
    def intersect(nums1: List[int], nums2: List[int]) -> List[int]:
        # Ensure seq1 is the shortest list and seq2 is the longest
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1

        # Sort the shorter list
        nums1.sort()

        # Initialize an empty list to store the intersection
        res = []

        # Iterate over elements in the longer list and perform binary search
        for num in nums2:
            # Perform binary search for num in nums1
            index = Solution.binary_search(nums1, num)

            # If num is found in nums1, add it to the result list and remove it from nums1
            if index != -1:
                res.append(num)
                del nums1[index]

        return res


# Test cases
if __name__ == '__main__':
    print(Solution.intersect(nums1=[1, 2, 2, 1], nums2=[2, 2]))  # Expected output: [2, 2]
    print(Solution.intersect(nums1=[4, 9, 5], nums2=[9, 4, 9, 8, 4]))  # Expected output: [4, 9]
