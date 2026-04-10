import heapq
from typing import List


class Solution:
    @staticmethod
    def kClosest(points: List[List[int]], k: int) -> List[List[int]]:
        # Create a min-heap
        heap = []

        # Iterate through each point in the list
        for point in points:
            x, y = point[0], point[1]
            # Calculate the squared Euclidean distance from the origin (0, 0)
            # Using squared distance to avoid unnecessary sqrt calculations
            distance = x ** 2 + y ** 2
            # Push the negative distance and point to the max-heap (by pushing negative distance we simulate max-heap
            # behavior in Python's min-heap)
            heapq.heappush(heap, (-distance, point))
            # If the heap size exceeds k, remove the farthest point
            if len(heap) > k:
                heapq.heappop(heap)

        # Extract the k closest points from the heap
        return [point for (_, point) in heap]


print(Solution.kClosest(points=[[3, 3], [5, -1], [-2, 4]], k=2))
