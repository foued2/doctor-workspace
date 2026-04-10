from typing import List


class Solution:
    @staticmethod
    def minOperations(nums: List[int]) -> int:
        # Initialize a variable to keep track of the total operations needed
        ans = 0

        # Initialize a variable to keep track of the required value for the next element
        required = nums[0]

        # Iterate through the list starting from the second element
        for i in range(1, len(nums)):
            # If the current number is less than or equal to the required value
            if nums[i] <= required:
                # Calculate the number of operations needed to make the current number greater than the required value
                ans += required - nums[i] + 1
                # Update the required value for the next element to be greater than the current number
                required += 1

            # Update the required value for the next element
            required = max(required, nums[i])

        return ans


if __name__ == '__main__':
    print(Solution.minOperations(nums=[1, 1, 1]))  # Output: 3
    print(Solution.minOperations(nums=[1, 5, 2, 4, 1]))  # Output: 6 (Operations needed: [1->2], [5->6], [2->5],
    # [4->6], [1->6])
