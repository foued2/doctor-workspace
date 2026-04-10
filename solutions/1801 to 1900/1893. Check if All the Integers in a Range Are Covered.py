from typing import List


class Solution:
    @staticmethod
    def isCovered(ranges: List[List[int]], left: int, right: int) -> bool:
        # Create an empty set to hold all numbers that are covered by the ranges
        nums = set()

        # Loop through each interval in the list of ranges
        for interval in ranges:
            # Add each number in the current interval to the set 'nums'
            for num in range(interval[0], interval[-1] + 1):
                nums.add(num)

        # Loop through each number in the range from 'left' to 'right' inclusive
        for num in range(left, right + 1):
            # If any number in this range is not in the set 'nums', return False
            if num not in nums:
                return False

        # If all numbers in the range from 'left' to 'right' are in the set 'nums', return True
        return True


print(Solution.isCovered(ranges=[[1, 10], [10, 20]], left=21, right=21))


class Solution:
    @staticmethod
    def isCovered(ranges: List[List[int]], left: int, right: int) -> bool:
        # Create an array to record the increments and decrements at specific points
        # We assume the maximum number is 50 based on the problem constraints (1 <= left <= right <= 50)
        max_val = 51
        diff = [0] * (max_val + 1)

        # Process each interval in the ranges
        for interval in ranges:
            start, end = interval
            # Increment the start of the interval
            diff[start] += 1
            # Decrement the point after the end of the interval
            if end + 1 <= max_val:
                diff[end + 1] -= 1

        # Build the prefix sum array to reflect the number of active coverages at each point
        prefix_sum = [0] * (max_val + 1)
        prefix_sum[0] = diff[0]
        for i in range(1, max_val + 1):
            prefix_sum[i] = prefix_sum[i - 1] + diff[i]

        # Check if all numbers in the range [left, right] are covered
        for num in range(left, right + 1):
            if prefix_sum[num] <= 0:
                return False

        return True
