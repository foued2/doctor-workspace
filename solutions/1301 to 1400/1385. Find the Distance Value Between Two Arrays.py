from typing import List
import bisect


class Solution:
    @staticmethod
    def findTheDistanceValue(arr1: List[int], arr2: List[int], d: int) -> int:
        ans = 0  # Initialize the counter for distance values

        # Iterate over each element in arr1
        for a in arr1:
            valid = True  # Assume the element is valid initially

            # Iterate over each element in arr2
            for b in arr2:
                # Check if the absolute difference is within the distance d
                if abs(a - b) <= d:
                    valid = False  # Mark the element as invalid
                    break  # No need to check further, move to the next element in arr1

            # If the element remained valid, increment the counter
            if valid:
                ans += 1

        return ans  # Return the count of valid elements


# Example usage:
arr1 = [4, 5, 8]
arr2 = [10, 9, 1, 8]
d = 2
solution = Solution()
print(solution.findTheDistanceValue(arr1, arr2, d))  # Output: 2


class Solution:
    @staticmethod
    def findTheDistanceValue(arr1: List[int], arr2: List[int], d: int) -> int:
        # Sort arr2 to use binary search
        arr2.sort()
        ans = 0  # Initialize the counter for distance values

        # Iterate over each element in arr1
        for a in arr1:
            # Use binary search to find the insertion point for 'a' in arr2
            pos = bisect.bisect_left(arr2, a)

            # Check if the element before the insertion point is within distance d
            if pos > 0 and abs(a - arr2[pos - 1]) <= d:
                continue

            # Check if the element at the insertion point is within distance d
            if pos < len(arr2) and abs(a - arr2[pos]) <= d:
                continue

            # If both conditions above are false, the element is valid
            ans += 1

        return ans  # Return the count of valid elements


# Example usage:
arr1 = [4, 5, 8]
arr2 = [10, 9, 1, 8]
d = 2
solution = Solution()
print(solution.findTheDistanceValue(arr1, arr2, d))  # Output: 2
