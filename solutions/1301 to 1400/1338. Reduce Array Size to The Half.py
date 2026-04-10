import heapq
from collections import Counter
from typing import List


class Solution:
    @staticmethod
    def minSetSize(arr: List[int]) -> int:
        """
        Heap, Max heap
        Finds the minimum number of unique integers to remove from the array
        such that at least half of the integers are removed.
        """
        n = len(arr)
        # Initialize the answer variable to count the number of sets to remove
        ans = 0
        # Initialize the count of removed elements
        count = 0

        # Create a Counter object to count the frequency of each integer in the array
        counter = Counter(arr)

        # Create a max-heap (by negating the frequencies)
        # max_heap will contain the frequencies of each unique integer in arr
        max_heap = list(-value for value in counter.values())
        heapq.heapify(max_heap)  # Convert the list to a heap

        # Remove elements until at least half of the array is removed
        while count < (n // 2):
            # Pop the most frequent element from the heap
            count += -heapq.heappop(max_heap)  # Add the positive frequency
            ans += 1  # Increment the number of sets removed

        return ans


print(Solution.minSetSize(arr=[3, 3, 3, 3, 5, 5, 5, 2, 2, 7]))
