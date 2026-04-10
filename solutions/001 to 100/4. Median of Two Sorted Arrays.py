# Import List from typing module for type hinting
from typing import List


# Define Solution class
class Solution:
    # Define function findMedianSortedArrays with two parameters nums1 and nums2
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        # Get the length of nums1
        n1 = len(nums1)
        # Get the length of nums2
        n2 = len(nums2)
        # Check if the length of nums1 is greater than the length of nums2 If yes, call the function
        # findMedianSortedArrays again with swapped parameters (for binary search optimization)
        if n1 > n2:
            return self.findMedianSortedArrays(nums2, nums1)
        # Get the total length of both arrays
        n = n1 + n2
        # Calculate the middle element index for a combined sorted array
        left = (n + 1) // 2
        # Start of nums1 for binary search 
        low = 0
        # End of nums1 for binary search
        high = n1
        # Binary search in nums1
        while low <= high:
            # Find mid-index value of nums1
            mid1 = (low + high) // 2
            # Corresponding mid-index value in a combined sorted array
            mid2 = left - mid1
            # Initializing left halves to negative infinity and right halves to positive infinity
            l1, l2, r1, r2 = float("-inf"), float("-inf"), float("inf"), float("inf")
            # If mid-index is not end of an array then r1 is value at mid1 in nums1
            if mid1 < n1:
                r1 = nums1[mid1]
            # If mid-index is not end of an array then r2 is value at mid2 in nums2
            if mid2 < n2:
                r2 = nums2[mid2]
            # If mid-index is not start of an array, then l1 is value at a left of mid in nums1
            if mid1 - 1 >= 0:
                l1 = nums1[mid1 - 1]
            # If mid-index is not start of an array, then l2 is value at a left of mid in nums2
            if mid2 - 1 >= 0:
                l2 = nums2[mid2 - 1]
            # If max between l1 and l2 is less or equal to min between r1 and r2
            if l1 <= r2 and l2 <= r1:
                # If n is odd, return max of l1 and l2
                if n % 2 == 1:
                    return max(l1, l2)
                # If n is even, return average between max of l1 and l2 and min of r1 and r2
                else:
                    return (float(max(l1, l2)) + float(min(r1, r2))) / 2.0
            # If l1 > r2, move left index
            if l1 > r2:
                high = mid1 - 1
            # If l2 > r1, move right index
            else:
                low = mid1 + 1
        # If the arrays do not intersect, return 0
        return 0


solution = Solution()
median = solution.findMedianSortedArrays([1, 2, 3, 8, 10, 20], [2, 5, 6])
print(median)
