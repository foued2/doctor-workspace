from typing import List
import heapq


class Solution:
    @staticmethod
    def lastStoneWeight(stones: List[int]) -> int:
        # Calculate the length of the stones' list
        n = len(stones)
        # Continue the process until there is only one stone left
        while n > 1:
            # Sort the stones list in descending order
            stones.sort(reverse=True)
            # If the two heaviest stones are of equal weight, remove them from the list
            if stones[0] == stones[1]:
                stones.pop(0)
                stones.pop(0)
                n -= 2  # Decrement the count of stones by 2
            else:
                # If the two heaviest stones are not of equal weight, smash them together and update the second
                # stone's weight
                stones[1] = abs(stones[0] - stones[1])
                # Remove the first stone from the list
                stones.pop(0)
                n -= 1  # Decrement the count of stones by 1

        # If there is exactly one stone left, return its weight, otherwise return 0
        return stones[0] if n == 1 else 0


# Test the function with the provided testcase
print(Solution.lastStoneWeight([7, 6, 7, 6, 9]))


class Solution:
    @staticmethod
    def lastStoneWeight(stones: List[int]) -> int:
        """
        Heap priority queue, heapq module
        """
        # Convert the list of stones to a max heap with negated values
        maxHeap = [-s for s in stones]
        # Convert the list to a heap in-place
        heapq.heapify(maxHeap)
        # Continue the process until there is only one stone left
        while len(maxHeap) > 1:
            # Extract the two heaviest stones from the heap
            first = heapq.heappop(maxHeap) * -1
            second = heapq.heappop(maxHeap) * -1
            # If the two heaviest stones are not of equal weight, smash them together and update the heap
            if first != second:
                first -= second
                heapq.heappush(maxHeap, -first)

        # Return the weight of the last remaining stone, if any
        return maxHeap[0] * -1 if maxHeap else 0


print(Solution.lastStoneWeight([7, 6, 7, 6, 9]))
