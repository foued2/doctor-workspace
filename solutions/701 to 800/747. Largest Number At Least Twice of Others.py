from typing import List


class Solution:
    @staticmethod
    def dominantIndex(nums: List[int]) -> int:
        # Sort the list to find the largest element
        sorted_nums = sorted(nums)
        # Get the index of the largest element in the original list
        largest_index = nums.index(sorted_nums[-1])

        # Iterate over the sorted list except for the largest element
        for num in sorted_nums[:-1]:
            # If any number is greater than half of the largest element, return -1
            if num > (sorted_nums[-1] // 2):
                return -1

        # If the largest element satisfies the dominance condition, return its index
        return largest_index


print(Solution.dominantIndex(nums=[3, 6, 1, 0]))
