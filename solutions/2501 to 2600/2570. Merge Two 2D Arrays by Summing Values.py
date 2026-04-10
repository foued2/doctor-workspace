import bisect
from typing import List


class Solution:
    @staticmethod
    def mergeArrays(nums1: List[List[int]], nums2: List[List[int]]) -> List[List[int]]:
        # Initialize an empty result list
        res = []

        # Create a dictionary to keep track of the sums of elements with the same first element
        counter1 = {}

        # Extend nums1 with elements from nums2
        nums1.extend(nums2)

        # Iterate over the combined list
        for num in nums1:
            # If the first element of the list is already in the dictionary, add the second element to the existing sum
            if num[0] in counter1:
                counter1[num[0]] += num[1]
            else:
                # Otherwise, create a new entry in the dictionary with the first element as the key and the second
                # element as the value
                counter1[num[0]] = num[1]

        # Iterate over the dictionary items
        for key, value in counter1.items():
            # Insert each key-value pair into the result list, maintaining sorted order using bisect.insort()
            bisect.insort(res, [key, value])

        # Return the sorted result list
        return res


print(Solution.mergeArrays(nums1=[[1, 2], [2, 3], [4, 5]], nums2=[[1, 4], [3, 2], [4, 1]]))
