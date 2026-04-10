from typing import List


class Solution:
    @staticmethod
    def search(nums: List[int], target: int) -> int:

        low, high = 0, len(nums) - 1

        middle = (low + high) // 2
        if nums[middle] == target:
            return middle
        while middle < len(nums) - 1 and nums[middle] < nums[middle + 1]:
            if nums[middle + 1] == target:
                return middle + 1
            middle += 1
        else:
            high = ((low + high) // 2) - 1
            low = middle + 1
        while low < len(nums):
            if nums[low] == target:
                return low
            low += 1
        while high >= 0:
            if nums[high] == target:
                return high
            high -= 1

        return -1

    print(search([1], 1))


class solution:
    @staticmethod
    def search(nums: List[int], target: int) -> int:
        # Initialize pointers for binary search
        low, high = 0, len(nums) - 1

        # Perform binary search
        while low <= high:
            # Calculate middle index
            mid = (low + high) // 2

            # Check if a middle element is the target
            if nums[mid] == target:
                return mid

            # Determine which side of the array is sorted
            if nums[low] <= nums[mid]:
                # The Left side is sorted
                if nums[low] <= target < nums[mid]:
                    high = mid - 1
                else:
                    low = mid + 1
            else:
                # The Right side is sorted
                if nums[mid] < target <= nums[high]:
                    low = mid + 1
                else:
                    high = mid - 1

        # Target not found in the array
        return -1
