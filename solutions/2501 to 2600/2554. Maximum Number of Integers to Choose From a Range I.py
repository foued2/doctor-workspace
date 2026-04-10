from typing import List

class Solution:
    @staticmethod
    def maxCount(banned: List[int], n: int, maxSum: int) -> int:
        # Define a helper function to perform binary search
        def helperBinarySearch(nums: List[int], k: int) -> bool:
            # Initialize the left and right pointers for binary search
            left, right = 0, len(nums) - 1
            # Continue searching while the left pointer is less than or equal to the right pointer
            while left <= right:
                # Calculate the middle index
                mid = (left + right) // 2
                # Check if the middle element is equal to the target number
                if nums[mid] == k:
                    # Return False if the number is found in the banned list
                    return False
                # If the middle element is greater than the target number, search the left half
                elif nums[mid] > k:
                    right = mid - 1
                # If the middle element is less than the target number, search the right half
                else:
                    left = mid + 1
            # Return True if the number is not found in the banned list
            return True

        # Sort the banned list to ensure binary search works correctly
        banned.sort()

        # Initialize the count of valid numbers to 0
        ans = 0
        # Iterate over the range from 1 to n (inclusive)
        for num in range(1, n + 1):
            # Check if the current number is not banned using the helper function
            if helperBinarySearch(banned, num):
                # Check if adding the current number would exceed maxSum
                if maxSum >= num:
                    # Increment the count of valid numbers
                    ans += 1
                    # Subtract the current number from the maxSum
                    maxSum -= num
                else:
                    # If the number exceeds maxSum, break the loop
                    break
        # Return the total count of valid numbers
        return ans


print(Solution.maxCount(
    banned=[176, 36, 104, 125, 188, 152, 101, 47, 51, 65, 39, 174, 29, 55, 13, 138, 79, 81, 175, 178, 42, 108, 24, 80,
            183, 190, 123, 20, 139, 22, 140, 62, 58, 137, 68, 148, 172, 76, 173, 189, 151, 186, 153, 57, 142, 105, 133,
            114, 165, 118, 56, 59, 124, 82, 49, 94, 8, 146, 109, 14, 85, 44, 60, 181, 95, 23, 150, 97, 28, 182, 157, 46,
            160, 155, 12, 67, 135, 117, 2, 25, 74, 91, 71, 98, 127, 120, 130, 107, 168, 18, 69, 110, 61, 147, 145, 38],
    n=3016, maxSum=240))
