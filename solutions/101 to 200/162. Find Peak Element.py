from typing import List


class Solution:
    @staticmethod
    def findPeakElement(nums: List[int]) -> int:
        # Get the length of the input list
        n = len(nums)

        # Check if the list has only one element
        if n == 1:
            return 0  # There's only one element, so it's the peak

        # Initialize start and end pointers for binary search
        start, end = 0, n - 1

        # Check if the first element is a peak
        if nums[0] > nums[1]:
            return 0
        # Check if the last element is a peak
        elif nums[-1] > nums[-2]:
            return n - 1

        # Perform binary search to find the peak element
        while start < end:
            # Calculate the mid-index
            mid = (start + end) // 2

            # If the middle element is greater than the next one, move end pointer to mid
            if nums[mid] > nums[mid + 1]:
                end = mid
            # Otherwise, move a start pointer to mid + 1
            else:
                start = mid + 1

        # Return the start pointer as the index of the peak element
        return start


if __name__ == '__main__':
    print(Solution.findPeakElement(nums=[1, 2, 1, 3, 5, 6, 4]))
    print(Solution.findPeakElement([4, 4, 4, 4]))