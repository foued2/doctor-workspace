from typing import List


class Solution:
    @staticmethod
    def containsDuplicate(nums: List[int]) -> bool:
        # Create an empty dictionary to store the frequency of each number
        table = {}

        # Iterate through each number in the list
        for num in nums:
            # Increment the frequency count of the current number in the dictionary
            # If the number is not present, default to 0 and then increment by 1
            table[num] = table.get(num, 0) + 1

            # If the frequency count of the current number is greater than 1,
            # it indicates that the number has been encountered more than once
            if table[num] > 1:
                # Return True to indicate the presence of duplicates
                return True

        # If no duplicates are found after iterating through the entire list,
        # return False to indicate that no duplicates exist
        return False


print(Solution.containsDuplicate(nums=[1, 2, 3, 1]))


# def quicksort(nums):
#     """
#     Quicksort algorithm implementation.
#
#     Parameters:
#     - nums: A list of comparable elements to be sorted.
#
#     Returns:
#     - Sorted list in ascending order.
#     """
#
#     # Check if the array has only one element or empty
#     if len(nums) <= 1:
#         return nums
#
#     # Select a pivot element (usually the last element)
#     pivot = nums[-1]
#
#     # Initialize left and right partitions
#     left_partition = []
#     right_partition = []
#
#     # Partitioning step: divide the array into two partitions
#     for element in nums[:-1]:
#         # Elements less than or equal to the pivot go to the left partition
#         if element <= pivot:
#             left_partition.append(element)
#         # Elements greater than the pivot go to the right partition
#         else:
#             right_partition.append(element)
#
#     # Recursively sort the left and right partitions
#     left_sorted = quicksort(left_partition)
#     right_sorted = quicksort(right_partition)
#
#     # Concatenate the sorted partitions with the pivot in between
#     return left_sorted + [pivot] + right_sorted
