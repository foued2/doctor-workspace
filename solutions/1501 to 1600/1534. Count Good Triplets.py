from typing import List
from bisect import insort, bisect_left, bisect_right


class Solution:
    @staticmethod
    def countGoodTriplets(arr: List[int], a: int, b: int, c: int) -> int:
        # Get the length of the array
        n = len(arr)
        # Initialize the answer to 0
        ans = 0

        # Loop through the array backwards, starting from the second last element
        for j in range(n - 2, -1, -1):
            # Create a list to store the differences that satisfy the condition with b
            arr_b = []

            # Loop through the elements after j
            for k in range(j + 1, n):
                # Calculate the difference between arr[j] and arr[k]
                diff = arr[j] - arr[k]
                # Check if the absolute difference is less than or equal to b
                if abs(diff) <= b:
                    # Insert the difference into the sorted list arr_b
                    insort(arr_b, diff)

            # Loop through the elements before j
            for i in range(j):
                # Calculate the difference between arr[i] and arr[j]
                diff = arr[i] - arr[j]
                # Check if the absolute difference is less than or equal to a
                if abs(diff) <= a:
                    # Find the range of indices in arr_b where the difference with diff is within the bounds of c
                    lower = bisect_left(arr_b, -c - diff)
                    upper = bisect_right(arr_b, c - diff)
                    # Increment the answer by the number of valid differences
                    ans += upper - lower

        # Return the total count of good triplets
        return ans


print(Solution.countGoodTriplets(arr=[7, 3, 7, 3, 12, 1, 12, 2, 3], a=5, b=8, c=1))
