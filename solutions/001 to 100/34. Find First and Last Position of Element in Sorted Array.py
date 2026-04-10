from typing import List


# Define a class named Solution to encapsulate the searchRange method.
class Solution:

    # Define a static method searchRange that takes a list of integers (nums) and an integer (target) as parameters,
    # and returns a list of two integers representing the first and last occurrences of the target in the input list.
    @staticmethod
    def searchRange(nums: List[int], target: int) -> List[int]:

        # Define a helper function findFirst that takes a list of integers (nums1) and an integer (target1) as
        # parameters, and returns the index of the first occurrence of target1 in nums1. If not found, return -1.
        def findFirst(nums, target1):
            left, right = 0, len(nums) - 1

            # Implement binary search to find the first occurrence of target1.
            while left <= right:
                mid = left + (right - left) // 2
                if nums[mid] == target1:
                    if mid == 0 or nums[mid - 1] != target1:
                        return mid
                    else:
                        right = mid - 1
                elif nums[mid] < target1:
                    left = mid + 1
                else:
                    right = mid - 1
            return -1

        # Define a helper function findLast that takes a list of integers (nums2) and an integer (target2) as
        # parameters, and returns the index of the last occurrence of target2 in nums2. If not found, return -1.
        def findLast(nums, target2):
            left, right = 0, len(nums) - 1

            # Implement binary search to find the last occurrence of target2.
            while left <= right:
                mid = left + (right - left) // 2
                if nums[mid] == target2:
                    if mid == len(nums) - 1 or nums[mid + 1] != target2:
                        return mid
                    else:
                        left = mid + 1
                elif nums[mid] < target2:
                    left = mid + 1
                else:
                    right = mid - 1
            return -1

        # Call the helper functions to find the first and last occurrences of the target in the input list.
        first = findFirst(nums, target)
        last = findLast(nums, target)

        # Return a list containing the first and last occurrences of the target.
        return [first, last]


# Create an instance of the Solution class and call the searchRange method with a sample input.
print(Solution.searchRange([2, 2], 2))
