from typing import List


class Solution:
    @staticmethod
    def maximumCount(nums: List[int]) -> int:
        # Define a binary search function to find the count of elements smaller than a given pivot
        def binary_search(pivot, nums):
            # Initialize left and right pointers for binary search
            left, right = 0, len(nums) - 1
            # Perform binary search
            while left <= right:
                mid = (left + right) // 2  # Calculate the mid-index
                # If the element at mid is less than or equal to the pivot, move the right pointer
                if nums[mid] <= pivot:
                    left = mid + 1
                # If the element at mid is greater than the pivot, move the left pointer
                else:
                    right = mid - 1
            # Return the left pointer, which represents the count of elements smaller than the pivot
            return left

        # Calculate the maximum count of occurrences of a number smaller than its index
        # by finding the count of elements smaller than -1 and the count of elements smaller than 0
        return max(binary_search(-1, nums), len(nums) - binary_search(0, nums))


print(Solution.maximumCount(nums=[-3, -2, -1, 0, 0, 1, 2]))
