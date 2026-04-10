from typing import List


class Solution:
    @staticmethod
    def findKthPositive(arr: List[int], k: int) -> int:
        """
        Binary search
        """
        # Initialize left and right pointers for binary search
        left, right = 0, len(arr) - 1

        # Perform binary search
        while left <= right:
            mid = (left + right) // 2
            # The number of positive integers missing until index mid
            missing = arr[mid] - (mid + 1)

            if missing < k:
                # If fewer than k numbers are missing up to index mid,
                # the k-th missing number must be after index mid
                left = mid + 1
            else:
                # If k or more numbers are missing up to index mid,
                # the k-th missing number is at index mid or before
                right = mid - 1

        # At this point, left is the smallest index such that the number of missing integers
        # up to that point is at least k. The k-th missing number is found by:
        # left + k is the count of all numbers up to that index minus the number of elements in arr up to that index
        return left + k


# Example usage:
arr = [2, 3, 4, 7, 11]
k = 5
solution = Solution()
print(solution.findKthPositive(arr, k))  # Output: 9

print(Solution.findKthPositive(arr=[2, 3, 4, 7, 11], k=5))
