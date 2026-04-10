import heapq  # Import the heapq module for working with heaps

from typing import List  # Import List type hint for clarity


class Solution:
    @staticmethod
    def minPairSum(nums: List[int]) -> int:
        # Get the length of the input list
        n = len(nums)

        # Sort the list `nums` in ascending order
        nums = sorted(nums)

        # Create an empty list `res` to be used as a min-heap
        res = []

        # Convert the empty list `res` into a min-heap using heapq.heapify
        heapq.heapify(res)

        # Loop through the first half of the sorted list (`n // 2` iterations)
        for i in range(n // 2):
            # Calculate the sum of the element at index `i` and its opposite end in the sorted list
            # Negate the sum to make it a minimum value for the min-heap
            sum_to_heap = -(nums[i] + nums[-(i + 1)])

            # Push the negated sum onto the min-heap `res`
            heapq.heappush(res, sum_to_heap)

        # Pop the minimum element (smallest pair sum) from the min-heap
        ans = heapq.heappop(res)

        # Remove the negation used earlier (since heaps deal with min values)
        ans *= -1

        # Return the calculated minimum pair sum
        return ans


print(Solution.minPairSum(nums=[3, 5, 2, 3]))
