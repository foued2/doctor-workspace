from typing import List


class Solution:
    @staticmethod
    def peakIndexInMountainArray(arr: List[int]) -> int:
        """
        Binary search
        """
        # Get the length of the input array
        n = len(arr)

        # Initialize the left and right pointers for binary search
        left = 1
        right = n - 2  # Excluding the first and last elements since they can't be peaks

        # Perform binary search within the range [left, right]
        while left <= right:
            # Calculate the middle index
            mid = (right + left) // 2

            # Check if the element at the middle index is greater than its neighbors
            if arr[mid - 1] < arr[mid] > arr[mid + 1]:
                # If it's a peak, return its index
                return mid
            elif arr[mid - 1] < arr[mid] < arr[mid + 1]:
                # If the element at mid is less than its right neighbor, move the left pointer to mid + 1
                left = mid + 1
            else:
                # If the element at mid is less than its left neighbor, move the right pointer to mid - 1
                right = mid - 1


print(Solution.peakIndexInMountainArray(arr=[0, 2, 1, 0]))
