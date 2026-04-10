# EASY // ARRAY // TWO POINTERS (First / Tracker)

from typing import List


# Define a class Solution which is a standard naming convention in LeetCode problems.
class Solution:

    # Define a function that takes a list of integers and returns an integer,
    # The list represents the input array, and the returned integer is the new length of an array
    # after removing duplicates in-place.
    @staticmethod
    def removeDuplicates(nums: List[int]) -> int:

        # Exception handling: if the list is empty, we return 0 as there are no elements to the process
        if not nums:
            return 0

        # We initialize the first pointer (i) at index 0; this pointer will track where the next
        # unique number should be placed.
        i = 0

        # Now, we start iterating over the list. 'j' is the second pointer that scans through the list.
        # We start this from index 1, because we already consider the first element (at index 0) unique.
        for j in range(1, len(nums)):

            # If the number at the current position of the first pointer does not equal
            # the number at the current position of the second pointer, we have found a new unique number.
            if nums[i] != nums[j]:
                # When a new unique number is found, increment-first pointer (i)
                i += 1

                # We place the new unique number at the position next to the last unique number.
                # This is achieved by assigning the number at the position of the second pointer (nums[j])
                # to the position of the first pointer (nums[i]).
                nums[i] = nums[j]

        # We return i + 1 as the new length of the array. '+1' is necessary because
        # we start counting length from 1, whereas indexes in lists start from 0.
        return i + 1, nums

    print(removeDuplicates([1, 2, 3, 3, 0, 1]))