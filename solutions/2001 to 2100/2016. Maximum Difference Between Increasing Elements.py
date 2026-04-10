from typing import List


class Solution:
    @staticmethod
    def maximumDifference(nums: List[int]) -> int:
        """
        Prefix min
        """
        # Initialize max difference as 0 (we will update this as we find larger differences)
        max_diff = 0

        # Initialize the minimum number to the first element in the list
        min_num = nums[0]

        # Iterate through each number in the list starting from the second element
        for i in range(1, len(nums)):
            # Update the minimum number if the current number is smaller than the current minimum
            min_num = min(min_num, nums[i])

            # Calculate the difference between the current number and the minimum number seen so far
            current_diff = nums[i] - min_num

            # Update the maximum difference if the current difference is larger
            max_diff = max(max_diff, current_diff)

            # If max_diff is still 0, it means no valid pair was found, so return -1
        return max_diff if max_diff > 0 else -1


print(Solution.maximumDifference(
    nums=[166, 140, 78, 413, 174, 266, 166, 280, 89, 103, 87, 236, 365, 312, 413, 396, 292, 339, 67, 16, 247, 232, 426,
          203, 104, 435, 205, 395, 322, 70, 436, 451, 184, 102, 419, 519, 271, 41, 44, 256, 488, 16, 393, 302, 434, 238,
          229, 148, 189, 364, 237, 7]))
