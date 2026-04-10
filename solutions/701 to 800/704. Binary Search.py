from typing import List


class Solution:
    @staticmethod
    def search(nums: List[int], target: int) -> int:
        # Initialize left and right pointers for binary search
        left, right = 0, len(nums) - 1

        # Binary search loop
        while left <= right:
            # Calculate the mid-index
            mid = (left + right) // 2

            # Check if the target is found at the mid-index
            if nums[mid] == target:
                return mid
            # If the target is greater than the mid-element, search the right half
            elif nums[mid] < target:
                left = mid + 1
            # If the target is smaller than the mid-element, search the left half
            else:
                right = mid - 1

        # If the target is not found, return -1
        return -1


# Test the function
if __name__ == '__main__':
    print(Solution.search(nums=[-1, 0, 3, 5, 9, 12], target=9))
