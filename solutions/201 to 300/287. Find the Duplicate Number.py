from typing import List


class Solution:
    @staticmethod
    def findDuplicate(nums: List[int]) -> int:
        # Initialize slow and fast pointers to the first element of the array
        slow = nums[0]
        fast = nums[0]

        # Phase 1: Cycle Detection
        while True:
            # Move the slow pointer one step forward
            slow = nums[slow]
            # Move the fast pointer two steps forward
            fast = nums[nums[fast]]
            # If the pointers meet, a cycle is detected, exit the loop
            if slow == fast:
                break

        # Phase 2: Meeting Point Detection (Cycle Start)
        # Reset the fast pointer to the first element of the array
        fast = nums[0]
        # Move both pointers at the same speed until they meet again
        while slow != fast:
            slow = nums[slow]
            fast = nums[fast]

        # The meeting point is the start of the cycle, which corresponds to the duplicate element
        return slow

    print(findDuplicate(nums=[4, 3, 1, 2, 2]))
