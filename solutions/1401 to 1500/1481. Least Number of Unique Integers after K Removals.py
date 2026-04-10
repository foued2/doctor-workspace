import heapq
from collections import Counter
from typing import List


class Solution:
    @staticmethod
    def findLeastNumOfUniqueInts(arr: List[int], k: int) -> int:
        """
        Heap, Min-heap
        """
        # Initialize the answer variable to count the unique integers remaining
        ans = 0

        # Create a Counter object to count the frequency of each integer in the array
        counter = Counter(arr)

        # Create a min-heap from the frequency values of the integer's
        # heap will contain the frequencies of each unique integer in arr
        heap = list(counter.values())
        heapq.heapify(heap)  # Convert the list to a min-heap

        # Remove elements from the heap while we can still remove k elements
        while k > 0 and heap:
            # Pop the smallest frequency element from the heap
            smallest_frequency = heapq.heappop(heap)

            # If k is less than the smallest frequency, we can't remove the entire group
            if k < smallest_frequency:
                # Since we can't remove this group entirely, the number of unique integers left increases by 1
                ans += 1
                break  # Break the loop as we can't remove any more elements

            # Subtract the smallest frequency from k, effectively removing that group of elements
            k -= smallest_frequency

        # Add the number of remaining unique integers in the heap to the answer
        ans += len(heap)

        # Return the total number of unique integers remaining after removing k elements
        return ans


print(Solution.findLeastNumOfUniqueInts(arr=[4, 3, 1, 1, 3, 3, 2], k=3))
