import heapq  # Importing heapq for heap operations
import math  # Importing math for mathematical functions
from typing import List  # Importing List from typing for type hinting


class Solution:
    @staticmethod
    def pickGifts(gifts: List[int], k: int) -> int:
        # Step 1: Convert the given list of gifts into a max heap
        # Since heapq is a min-heap by default, we use negative values to simulate a max-heap
        max_heap = [-pile for pile in gifts]

        # Step 2: Transform the list into a heap in-place
        heapq.heapify(max_heap)

        # Step 3: Perform the operation k times
        for _ in range(k):
            # Step 3.1: Pop the largest element from the heap (smallest negative value)
            # Multiplying by -1 converts it back to a positive number
            pile = heapq.heappop(max_heap) * -1

            # Step 3.2: Calculate the integer square root of the largest pile
            sqrt_pile = math.sqrt(pile)
            int_sqrt_pile = int(sqrt_pile)

            # Step 3.3: Push the negative of the new value back into the heap
            # This maintains the max-heap property by keeping values negative
            heapq.heappush(max_heap, -int_sqrt_pile)

        # Step 4: Calculate the final sum of the elements in the heap
        # Since all values in the heap are negative, summing them and multiplying by -1 gives the positive sum
        ans = -sum(max_heap)

        # Step 5: Return the final sum
        return ans


print(Solution.pickGifts(gifts=[25, 64, 9, 4, 100], k=4))
