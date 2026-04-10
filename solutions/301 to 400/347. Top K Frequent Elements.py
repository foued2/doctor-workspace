from typing import List
import heapq
from collections import Counter


class Solution:
    @staticmethod
    def topKFrequent(nums: List[int], k: int) -> List[int]:
        # Step 1: Use a Counter (Hash Table) to count the frequency of each element in the input array (Array).
        counts = Counter(nums)  # O(n), where n is the number of elements in nums

        # Step 2: Use a min heap (Heap) to keep track of the k most frequent elements.
        # Each element in the heap is a tuple (frequency, element).
        heap = []  # Initialize an empty heap
        for num, count in counts.items():  # Iterate through elements and their counts in the Counter
            # Push the element with its negative frequency onto the heap. Negative frequency is used to create a min
            # heap that stores elements with the highest frequency at the top.
            heapq.heappush(heap, (count, num))  # O(log k), where k is the size of the heap
            # If the size of the heap exceeds k, pop the smallest element (Divide and Conquer).
            if len(heap) > k:
                heapq.heappop(heap)  # O(log k)

        # Step 3: Extract the k most frequent elements from the heap.
        top_k = []  # Initialize an empty list to store the top k frequent elements
        while heap:
            # Pop the element with the highest negative frequency (Sorting).
            # The smallest element (with the lowest frequency) is popped first due to min heap property.
            count, num = heapq.heappop(heap)  # O(log k)
            # Append the element to the result.
            top_k.append(num)

        # Step 4: Return the top k frequent elements in descending order of frequency.
        return top_k[::-1]  # Reverse the list to get elements in descending order of frequency (Bucket Sort).


# Test the function
print(Solution.topKFrequent([1, 1, 1, 2, 2, 3], 2))  # Output: [1, 2]

#         table = {}
#         for num in nums:
#             table[num] = table.get(num, 0) + 1
#         print(table)
#         return sorted(table, key=table.get, reverse=True)[:k]
#
#     print(topKFrequent(nums=[4, 1, -1, 2, -1, 2, 3], k=2))
