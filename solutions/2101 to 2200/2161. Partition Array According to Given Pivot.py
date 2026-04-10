from typing import List


class Solution:
    @staticmethod
    def pivotArray(nums: List[int], pivot: int) -> List[int]:
        # Get the length of the input list
        n = len(nums)

        # Initialize three lists to hold elements less than, greater than, and equal to the pivot
        left = []
        right = []
        middle = []

        # Initialize a counter to iterate through the input list
        i = 0

        # Iterate over each element in the input list
        while i < n:
            if nums[i] < pivot:
                # If the current element is less than the pivot, add it to 'left' list
                left.append(nums[i])
            elif nums[i] > pivot:
                # If the current element is greater than the pivot, add it to 'right' list
                right.append(nums[i])
            else:
                # If the current element is equal to the pivot, add it to 'middle' list
                middle.append(nums[i])
            # Move to the next element
            i += 1

        # Concatenate the 'left', 'middle', and 'right' lists and return the result
        return left + middle + right


if __name__ == '__main__':
    # Example usage: Reordering the array such that elements less than the pivot come first, followed by elements equal to the pivot, and then elements greater than the pivot
    print(Solution.pivotArray(nums=[9, 12, 5, 10, 14, 3, 10], pivot=10))  # Output should be [9, 5, 3, 10, 10, 12, 14]