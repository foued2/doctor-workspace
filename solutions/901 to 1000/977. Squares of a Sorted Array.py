from typing import List


class Solution:
    @staticmethod
    def sortedSquares(nums: List[int]) -> List[int]:
        n = len(nums)
        result = [0] * n  # Initialize a result array

        left, right = 0, n - 1  # Initialize two pointers

        # Iterate over the result array from right to left
        for i in range(n - 1, -1, -1):
            # Compare absolute values of elements at indices left and right
            if abs(nums[left]) > abs(nums[right]):
                # If the absolute value of an element at left pointer is greater,
                # square it and place it at the end of the result array
                result[i] = nums[left] ** 2
                left += 1  # Move a left pointer to the right
            else:
                # If the absolute value of an element at right pointer is greater,
                # square it and place it at the end of the result array
                result[i] = nums[right] ** 2
                right -= 1  # Move a right pointer to the left

        return result


if __name__ == '__main__':
    print(Solution.sortedSquares([-4, -1, 0, 3, 10]))  # Output: [0, 1, 9, 16, 100]
