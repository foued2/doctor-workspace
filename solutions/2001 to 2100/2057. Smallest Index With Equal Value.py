from typing import List


class Solution:
    @staticmethod
    def smallestEqual(nums: List[int]) -> int:
        # Get the length of the input list
        n = len(nums)

        # Iterate through the list
        for i in range(n):
            # Check if the index 'i' modulo 10 is equal to the value at index 'i'
            if i % 10 == nums[i]:
                # If the condition is met, return the index 'i'
                return i

        # If no such index is found, return -1
        return -1


print(Solution.smallestEqual(nums=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]))
