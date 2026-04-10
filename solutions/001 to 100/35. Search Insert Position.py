# EASY // ARRAY // BINARY SEARCH (First / Last / Middle)

# Importing the List class from the typing module, which is used for type hinting in Python.
from typing import List


# Definition of the Solution class.
class Solution:
    # Definition of the static method 'searchInsert' that belongs to the Solution class.
    @staticmethod
    def searchInsert(nums: List[int], target: int) -> int:
        # Initialization of low and high pointers that will be used to perform the binary search.
        low, high = 0, len(nums) - 1

        # Binary search loop running until low is not greater than high.
        while low <= high:
            # Find the middle index. If the sum is odd, it will take the lower middle index.
            middle = (low + high) // 2

            # If the value at the middle index is equal to the target, returns the middle index.
            if nums[middle] == target:
                return middle
            # If the value at the middle index less than the target, update low to middle + 1.
            elif nums[middle] < target:
                low = middle + 1
            # Else, if the value at the middle index is greater than the target, update high to middle - 1.
            else:
                high = middle - 1

        # If the target can't be found in the list, return the point where the target should be inserted, i.e.,
        # where 'low' ended up.
        return low

    # Test the searchInsert function with an example. 200 is not found in the given list; thus the function would
    # return the index at which 200 can be inserted, i.e., at the end of the list (index 5).
    print(searchInsert([1], 22))  # Output: 5
    # Output: 2
    # Example
    # 2:
    #
    # Input: nums = [1, 3, 5, 6], target = 2
    # Output: 1
    # Example
    # 3:
    #
    # Input: nums = [1, 3, 5, 6], target = 7
    # Output: 4
