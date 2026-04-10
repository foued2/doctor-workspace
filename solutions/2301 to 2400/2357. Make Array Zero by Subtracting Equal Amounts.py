import heapq
from typing import List


class Solution:
    @staticmethod
    def minimumOperations(nums: List[int]) -> int:
        """
        Heap, operation on heap items
        """
        # Get the number of elements in the array
        n = len(nums)

        # Initialize the counter for the number of operations
        ans = 0

        # Convert the list into a heap to efficiently get the smallest element
        heapq.heapify(nums)

        # Loop until the heap is empty
        while n:
            # If the smallest element in the heap is zero
            if nums[0] == 0:
                # Remove the smallest element (which is zero)
                heapq.heappop(nums)
                # Decrease the count of elements
                n -= 1
            else:
                # Increment the operation counter
                ans += 1
                # Get the smallest element from the heap
                first = nums[0]

                # Subtract the smallest element from all remaining elements in the heap
                for i in range(n):
                    nums[i] -= first

            # Re-heapify the list to maintain the heap property after modification
            heapq.heapify(nums)

        # Return the total number of operations
        return ans


# Example usage
solution = Solution()
print(solution.minimumOperations([1, 5, 0, 3, 5]))  # Output: 3
print(solution.minimumOperations([0, 0, 0]))  # Output: 0
print(solution.minimumOperations([5, 1, 5]))  # Output: 2
