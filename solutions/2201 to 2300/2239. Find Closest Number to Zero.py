from typing import List


class Solution:
    @staticmethod
    def findClosestNumber(nums: List[int]) -> int:
        """
        Binary search
        """
        # Step 1: Sort the array to apply binary search
        nums.sort()

        # Step 2: Initialize pointers for binary search
        left, right = 0, len(nums) - 1

        # Step 3: Perform binary search to find the closest elements around zero
        while left <= right:
            mid = (left + right) // 2
            if nums[mid] < 0:
                # If the middle element is negative, move the left pointer
                left = mid + 1
            else:
                # If the middle element is positive, move the right pointer
                right = mid - 1

        # Step 4: Determine the closest number to zero
        # After the loop, left is the first positive number, and right is the last negative number

        # Handle edge cases where left or right might be out of bounds
        if left >= len(nums):
            return nums[right]
        if right < 0:
            return nums[left]

        # Compare the absolute values of the closest elements
        if abs(nums[left]) == abs(nums[right]):
            return max(nums[left], nums[right])
        else:
            return nums[left] if abs(nums[left]) < abs(nums[right]) else nums[right]


# Example usage
solution = Solution()
print(solution.findClosestNumber([3, -4, 2, -1, -2, 1, 4]))  # Output should be -1 or 1
