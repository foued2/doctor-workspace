import heapq
from typing import List


class Solution:
    @staticmethod
    def countGoodRectangles(rectangles: List[List[int]]) -> int:
        # Initialize a max heap to store the negative of the minimum side lengths of rectangles
        max_heap = []

        # Iterate through each rectangle
        for rectangle in rectangles:
            # Calculate the minimum side length of the current rectangle and push its negative to the heap
            min_side = min(rectangle)
            heapq.heappush(max_heap, -min_side)

        # The maximum side length (which is the negative of the smallest element in the max-heap)
        max_len = -max_heap[0]

        # Initialize the counter for rectangles that can form the largest possible square
        count = 0

        # Count how many times max_len appears in the heap
        while max_heap and -heapq.heappop(max_heap) == max_len:
            count += 1

        return count


print(Solution.countGoodRectangles(rectangles=[[2, 3], [3, 7], [4, 3], [3, 7]]))


class Solution:
    @staticmethod
    def countGoodRectangles(rectangles: List[List[int]]) -> int:
        # Initialize variables to track the maximum side length and its count
        max_len = 0
        max_count = 0

        # Iterate through each rectangle
        for rectangle in rectangles:
            # Calculate the minimum side length of the current rectangle
            curr_min = min(rectangle)

            # Update max_len and max_count accordingly
            if curr_min > max_len:
                max_len = curr_min
                max_count = 1
            elif curr_min == max_len:
                max_count += 1

        # Return the count of rectangles that can form the largest square
        return max_count
