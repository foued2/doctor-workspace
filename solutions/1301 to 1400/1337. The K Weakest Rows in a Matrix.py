import heapq
from typing import List


class Solution:
    @staticmethod
    def kWeakestRows(mat: List[List[int]], k: int) -> List[int]:
        """
        Binary search, array division, Heap, Heappush
        """
        def binary_search(row: List[int]) -> int:
            # Initialize the left and right pointers for the binary search
            left, right = 0, len(row) - 1

            # Continue searching while the left pointer does not cross the right pointer
            while left <= right:
                # Calculate the middle index in the current search range
                mid = left + (right - left) // 2

                # If the middle element is 1
                if row[mid] == 1:
                    # Move the search range to the right half
                    left = mid + 1
                else:
                    # Move the search range to the left half
                    right = mid - 1

            # Return the count of 1's in the row
            return left

        # Initialize an empty heap to store pairs of (count of 1s in row, row index)
        heap = []

        # Iterate over each row in the matrix
        for i, row in enumerate(mat):
            # Count the number of 1s in the current row
            count_ones = binary_search(row)

            # Push a tuple containing the count of 1s and the row index onto the heap
            heapq.heappush(heap, (count_ones, i))

        # Extract the k weakest rows from the heap,
        # Pop the smallest element (pair) from the heap k times, and extract the row index
        weakest = [heapq.heappop(heap)[1] for _ in range(k)]

        # Return the list of indices of the k weakest rows
        return weakest


# Test the function
mat = [[1, 1, 0, 0, 0],
       [1, 1, 1, 1, 0],
       [1, 0, 0, 0, 0],
       [1, 1, 0, 0, 0],
       [1, 1, 1, 1, 1]]
k = 3
print(Solution.kWeakestRows(mat, k))  # Output should be [2, 0, 3]
