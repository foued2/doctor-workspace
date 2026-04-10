from typing import List


class Solution:
    @staticmethod
    def maxDistance(nums1: List[int], nums2: List[int]) -> int:
        # Helper function to perform binary search
        def binary_search(nums, target, start):
            left, right = start, len(nums) - 1
            result = -1
            # Perform binary search to find the rightmost element >= target
            while left <= right:
                mid = left + (right - left) // 2
                if nums[mid] >= target:
                    result = mid
                    left = mid + 1  # Move right to find a larger candidate
                else:
                    right = mid - 1
            return result

        max_distance = 0  # Initialize max_distance to 0
        # Iterate over each element in nums1
        for i in range(len(nums1)):
            # Perform binary search on nums2 starting from index i
            index = binary_search(nums2, nums1[i], i)
            # Ensure an appropriate index was found
            if index != -1:
                # Calculate the distance and update max_distance
                max_distance = max(max_distance, index - i)

        return max_distance  # Return the maximum distance found


if __name__ == '__main__':
    # Test the function with the specified example
    print(Solution().maxDistance(nums1=[55, 30, 5, 4, 2], nums2=[100, 20, 10, 10, 5]))