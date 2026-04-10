from typing import List


class Solution:
    @staticmethod
    def numSubarrayProductLessThanK(nums: List[int], k: int) -> int:
        if k <= 1:
            return 0  # If k is less than or equal to 1, no subarray can satisfy the condition

        left = ans = 0  # Initialize pointers and the count of valid subarrays
        curr = 1  # Initialize the product of elements in the current subarray

        for right in range(len(nums)):
            curr *= nums[right]  # Update the product by multiplying with the next element

            # Shrink the window from the left until the product is less than k
            while curr >= k:
                curr //= nums[left]  # Remove the leftmost element from the product
                left += 1  # Move the left pointer

            # Every valid subarray ending at the current right pointer contributes (right - left + 1) subarrays
            ans += right - left + 1

        return ans  # Return the count of valid subarrays


if __name__ == '__main__':
    print(Solution.numSubarrayProductLessThanK(nums=[10, 5, 2, 6], k=100))
