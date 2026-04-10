from typing import List


class Solution:
    @staticmethod
    def pivotIndex(nums: List[int]) -> int:
        """
        Prefix sum
        """
        # Get the length of the input list
        n = len(nums)
        # Calculate the sum of all elements in the list
        right_sum = sum(nums)
        # Initialize the sum of elements to the left of the current index
        left_sum = 0

        # Iterate through each index in the list
        for i in range(n):
            # Decrement the right sum by the current element to get the sum of elements
            # to the right of the current index.
            right_sum -= nums[i]

            # If the sum of elements to the left of the current index is equal to the sum
            # of elements to the right of the current index, then we have found the pivot
            # index.
            if left_sum == right_sum:
                return i

            # Increment the left sum by the current element to move the window one position
            # to the right.
            left_sum += nums[i]

        # If no pivot index was found, return -1.
        return -1


if __name__ == '__main__':
    # Example usage
    print(Solution.pivotIndex(nums=[1, 1]))

