from typing import List


class Solution:
    @staticmethod
    def numberOfPoints(nums: List[List[int]]) -> int:
        # Initialize an empty set to store unique points
        res = set()

        # Iterate through each interval in nums
        for point in nums:
            # Create a set of all points in the current interval
            interval_points = set(i for i in range(point[0], point[1] + 1))
            # Update the result set with the points in the current interval
            res |= interval_points

        # Return the number of unique points
        return len(res)


print(Solution.numberOfPoints(nums=[[3, 6], [1, 5], [4, 7]]))


class Solution:
    @staticmethod
    def numberOfPoints(nums: List[List[int]]) -> int:
        """
        Prefix sum
        """
        # Sort intervals by the starting point
        nums.sort()

        # Initialize the first interval
        current_start, current_end = nums[0]
        total_points = 0

        for i in range(1, len(nums)):
            start, end = nums[i]
            if start <= current_end:
                # Overlapping intervals, merge them
                current_end = max(current_end, end)
            else:
                # No overlap, add the length of the current interval
                total_points += (current_end - current_start + 1)
                # Move to the next interval
                current_start, current_end = start, end

        # Add the last interval
        total_points += (current_end - current_start + 1)

        return total_points


# Example usage
nums = [[1, 3], [2, 6], [8, 10], [15, 18]]
solution = Solution()
print(solution.numberOfPoints(nums))  # Output should be 9 (1-6 and 8-10 and 15-18)
