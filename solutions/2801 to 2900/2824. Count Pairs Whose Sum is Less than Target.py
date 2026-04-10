from typing import List


class Solution:
    @staticmethod
    def countPairs(nums: List[int], target: int) -> int:
        """
        Two pointers
        """
        # Sort the input list to facilitate counting pairs
        nums.sort()

        # Initialize pointers for the leftmost (i) and rightmost (j) elements
        j = len(nums) - 1
        i = 0

        # Initialize a variable to store the count of pairs satisfying the condition
        pair_count = 0

        # Iterate through the list with two pointers
        while i < j:
            # Check if the sum of the current pair is less than the target
            if nums[i] + nums[j] < target:
                # If so, increment the count by the number of elements between i and j
                pair_count += j - i
                # Move the left pointer to the right
                i += 1
            else:
                # If not, move the right pointer to the left
                j -= 1

        # Return the total count of pairs satisfying the condition
        return pair_count


if __name__ == '__main__':
    print(Solution.countPairs(nums=[-6, 2, 5, -2, -7, -1, 3], target=-2))


class Solution:
    @staticmethod
    def countPairs(nums: List[int], target: int) -> int:
        """
        Binary search
        """
        # Sort the input list
        nums.sort()

        # Initialize a variable to store the count of pairs satisfying the condition
        pair_count = 0

        # Iterate through the list of numbers
        for i in range(len(nums)):
            # Find the rightmost index such that nums[i] + nums[j] < target
            left = i + 1
            right = len(nums) - 1
            while left <= right:
                mid = (left + right) // 2
                if nums[i] + nums[mid] < target:
                    # If the sum is less than target, update the left pointer
                    left = mid + 1
                else:
                    # Otherwise, update the right pointer
                    right = mid - 1

            # Increment the count by the number of elements between i and right
            pair_count += right - i

        # Return the total count of pairs satisfying the condition
        return pair_count
