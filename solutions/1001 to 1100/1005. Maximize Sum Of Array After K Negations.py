from typing import List
import heapq


class Solution:
    @staticmethod
    def largestSumAfterKNegations(nums: List[int], k: int) -> int:
        # Create a min-heap from the given list of numbers
        heapq.heapify(nums)

        # Perform k negations
        for _ in range(k):
            # Extract the smallest element from the heap
            smallest = heapq.heappop(nums)
            # Negate it and push it back to the heap
            heapq.heappush(nums, -smallest)

        # Calculate the sum of the elements in the heap
        return sum(nums)


# Example usage
nums = [4, 2, 3]
k = 1
solution = Solution()
print(solution.largestSumAfterKNegations(nums, k))  # Output: 5

print(Solution.largestSumAfterKNegations(nums=[-2, 9, 9, 8, 4], k=5))

