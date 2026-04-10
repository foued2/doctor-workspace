from typing import List


class Solution:
    @staticmethod
    def validMountainArray(arr: List[int]) -> bool:
        n = len(arr)

        # A mountain array must have at least 3 elements
        if n < 3:
            return False

        # Initialize pointers for climbing up
        i = 0

        # Climb up the mountain until the peak
        while i + 1 < n and arr[i] < arr[i + 1]:
            i += 1

        # Peak can't be the first or last element
        if i == 0 or i == n - 1:
            return False

        # Climb down the mountain
        while i + 1 < n and arr[i] > arr[i + 1]:
            i += 1

        # If we reach the end, it means it is a valid mountain array
        return i == n - 1


# Example usage
arr = [0, 3, 2, 1]
print(Solution.validMountainArray(arr))  # Expected output: True

arr = [3, 5, 5]
print(Solution.validMountainArray(arr))  # Expected output: False

arr = [2, 1]
print(Solution.validMountainArray(arr))  # Expected output: False
