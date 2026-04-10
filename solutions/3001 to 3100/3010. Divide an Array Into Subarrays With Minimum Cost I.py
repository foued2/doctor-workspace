from typing import List
from heapq import heappush, heappushpop


class Solution:
    @staticmethod
    def minimumCost(nums: List[int]) -> int:
        # Create an empty heap (using a min-heap with negative values to simulate a max-heap)
        heap = []

        # Push the negative of the second element to the heap
        heappush(heap, -nums[1])

        # Push the negative of the third element to the heap
        heappush(heap, -nums[2])

        # Iterate through the remaining elements starting from the fourth element
        for num in nums[3:]:
            # Push the negative of the current element to the heap and pop the smallest (most negative)
            heappushpop(heap, -num)

        # Calculate the result as the first element minus the sum of the two largest elements (converted back to
        # positive)
        return nums[0] - heap[0] - heap[1]


# Example usage:
sol = Solution()
print(sol.minimumCost([10, 2, 3, 4, 5]))  # Example call to the function
