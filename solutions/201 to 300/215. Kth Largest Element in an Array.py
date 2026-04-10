from typing import List
import random


class Solution:
    @staticmethod
    def findKthLargest(nums: List[int], k: int) -> int:
        # Define the quickselect algorithm to find the kth largest element
        def quickselect(nums, k):
            # Initialize lists to store elements smaller, equal, and larger than the pivot
            small, equal, large = [], [], []
            # Choose a random pivot element from the nums array
            pivot = random.choice(nums)
            # Partition the array into three parts based on the pivot
            for num in nums:
                if num > pivot:
                    large.append(num)
                elif num == pivot:
                    equal.append(num)
                elif num < pivot:
                    small.append(num)

            # CASE-1: If the number of elements in the large array is greater than or equal to k,
            #         the kth largest element is in the large array
            if len(large) >= k:
                return quickselect(large, k)

            # CASE-2: If the number of elements in the large and equal arrays combined is less than k,
            #         the kth largest element is in the small array
            elif (len(large) + len(equal)) < k:
                return quickselect(small, k - (len(large) + len(equal)))

            # CASE-3: Otherwise, the pivot (and all elements in the equal array) is the kth largest element
            else:
                return pivot

        # Call the quickselect function with the input array nums and k
        return quickselect(nums, k)
