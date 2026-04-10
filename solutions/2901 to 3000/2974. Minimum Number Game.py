import heapq
from typing import List


class Solution:
    @staticmethod
    def numberGame(nums: List[int]) -> List[int]:
        # Sort the input list of numbers
        nums = sorted(nums)

        # Iterate over the sorted list in steps of 2
        for i in range(0, len(nums), 2):
            # Swap the current element with the next element
            nums[i], nums[i + 1] = nums[i + 1], nums[i]

        # Return the modified list
        return nums


print(Solution.numberGame(nums=[5, 4, 2, 3]))


class Solution:
    @staticmethod
    def numberGame(nums: List[int]) -> List[int]:
        """
        Heap, heappop
        """
        # Initialize an empty list to store the results
        arr = []

        # Convert the input list into a min heap
        heapq.heapify(nums)

        # Repeat the following steps while the min heap is not empty
        while nums:
            # Remove the two smallest elements from the min heap
            first, second = heapq.heappop(nums), heapq.heappop(nums)

            # Append the second-smallest element to the result list (Bob's move)
            arr.append(second)

            # Append the smallest element to the result list (Alice's move)
            arr.append(first)

        # Return the resulting array
        return arr


print(Solution.numberGame(nums=[2, 5]))
