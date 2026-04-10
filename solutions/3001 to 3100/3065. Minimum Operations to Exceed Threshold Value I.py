from typing import List


class Solution:
    @staticmethod
    def minOperations(nums: List[int], k: int) -> int:
        # Initialize a variable to count the operations
        count = 0

        # Iterate through the list
        for i in range(len(nums)):
            # Check if the current element is less than k
            if nums[i] < k:
                # If it is, increment the count of operations
                count += 1

        # Return the total count of operations
        return count


if __name__ == '__main__':
    print(Solution.minOperations(nums=[1, 1, 2, 4, 9], k=9))
