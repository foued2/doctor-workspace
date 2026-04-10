from collections import Counter
from typing import List


class Solution:
    @staticmethod
    def minOperations(nums: List[int], k: int) -> int:
        # Initialize the operation count
        operation_count = 0

        # Get the total number of elements in the list
        n = len(nums)

        # Create a Counter to count the occurrences of each number in the list
        table = Counter(nums)

        # Iterate over the list with both index and value
        for i, num in enumerate(nums):
            # Check if the current number appears more than once and is within the range [1, k]
            if table[num] > 1 and num <= k:
                # Decrement the count of the current number in the Counter
                table[num] -= 1
            elif table[num] == 1 and num <= k:
                # If the current number is the last occurrence and within the range [1, k]
                # Calculate the number of operations required
                operation_count = n - i
                break

        # Return the total number of operations required
        return operation_count


print(Solution.minOperations(nums=[3, 2, 5, 3, 1], k=3))


class Solution:
    @staticmethod
    def minOperations(nums: List[int], k: int) -> int:
        # Initialize the state bitmask and operation count
        state_bitmask = 0
        operation_count = 0

        # Calculate the goal bitmask for numbers 1 through k
        goal_bitmask = (1 << (k + 1)) - 2  # The binary representation will have bits 1 to k set to 1

        # Iterate until nums is empty
        while nums:
            # Increment the count of operations
            operation_count += 1

            # Pop the last number from the list
            current_num = nums.pop()

            # If the current number is less than or equal to k, update the state bitmask
            if current_num <= k:
                state_bitmask |= (1 << current_num)

            # Check if the state bitmask matches the goal bitmask
            if state_bitmask == goal_bitmask:
                # Return the count of operations when the goal is achieved
                return operation_count


print(Solution.minOperations(nums=[3, 2, 5, 3, 1], k=3))
