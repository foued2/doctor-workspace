import heapq
from typing import List


class Solution:
    @staticmethod
    def getFinalState(nums: List[int], k: int, multiplier: int) -> List[int]:
        """
        Heapq
        """
        heap = []

        # Step 1: Create a heap with tuples of (element, index)
        for i in range(len(nums)):
            heapq.heappush(heap, (nums[i], i))

        # Step 2: Perform the operation k times
        for _ in range(k):
            # Pop the smallest element along with its index
            num, idx = heapq.heappop(heap)
            # Push the modified element back into the heap
            heapq.heappush(heap, (num * multiplier, idx))

        # Step 3: Extract elements from the heap and restore to the original list
        for _ in range(len(nums)):
            num, idx = heapq.heappop(heap)
            nums[idx] = num

        return nums


# Usage
if __name__ == '__main__':
    print(Solution().getFinalState(nums=[2, 1, 3, 5, 6], k=5, multiplier=2))