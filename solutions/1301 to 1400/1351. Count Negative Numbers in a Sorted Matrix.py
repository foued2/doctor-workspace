from typing import List


class Solution:
    @staticmethod
    def countNegatives(grid: List[List[int]]) -> int:
        """
        Binary search
        """
        # Define a helper function to perform binary search within a row
        def binary_search(row: List[int]) -> int:
            left, right = 0, len(row) - 1
            while left <= right:
                mid = left + (right - left) // 2
                if row[mid] < 0:
                    # If the middle element is negative, move left to search for more negatives
                    right = mid - 1
                else:
                    # If the middle element is non-negative, move right to search for more negatives
                    left = mid + 1
            # Return the count of negative numbers in the row (number of elements to the right of 'left')
            return len(row) - left

        # Initialize a variable to store the total count of negative numbers
        count = 0
        # Iterate through each row in the grid
        for row in grid:
            # Accumulate the count of negative numbers in the current row using binary search
            count += binary_search(row)
        # Return the total count of negative numbers across all rows
        return count


if __name__ == '__main__':
    # Test the countNegatives method with a sample grid and print the result
    print(Solution.countNegatives(grid=[[4, 3, 2, -1], [3, 2, 1, -1], [1, 1, -1, -2], [-1, -1, -2, -3]]))
