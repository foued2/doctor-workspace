from typing import List


class Solution:
    @staticmethod
    def fixedPoint(arr: List[int]) -> int:
        """
        Binary search
        """
        # Initialize 'ans' with infinity to track the smallest index where arr[i] == i
        ans = float('inf')
        # Initialize the left and right pointers for binary search
        left, right = 0, len(arr) - 1

        # Perform binary search
        while left <= right:
            # Calculate the middle index
            mid = (left + right) // 2

            # Check if the middle element is a fixed point
            if arr[mid] == mid:
                # Update 'ans' to the smaller index if a fixed point is found
                ans = min(ans, mid)
                # Since we are looking for the smallest fixed point, continue searching to the left
                right = mid - 1
            # If the middle element is less than its index, search the right half
            elif arr[mid] < mid:
                left = mid + 1
            # If the middle element is greater than its index, search the left half
            else:
                right = mid - 1

        # If 'ans' is still infinity, no fixed point was found, return -1
        if ans == float('inf'):
            return -1
        # Otherwise, return the smallest fixed point index found
        else:
            return ans


print(Solution.fixedPoint(arr=[-10, -5, 0, 3, 7]))
