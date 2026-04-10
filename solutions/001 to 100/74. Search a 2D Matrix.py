from typing import List


class Solution:
    @staticmethod
    def searchMatrix(matrix: List[List[int]], target: int) -> bool:
        # Concatenate the first row of the matrix with all other elements in the matrix
        nums = [element for row in matrix for element in row]

        # Binary search implementation
        left, right = 0, len(nums) - 1
        while left <= right:
            mid = (left + right) // 2
            if nums[mid] == target:
                return True
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return False


# Test cases
if __name__ == '__main__':
    # Example test cases
    print(Solution.searchMatrix(matrix=[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], target=3))
    print(Solution.searchMatrix(matrix=[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], target=13))
