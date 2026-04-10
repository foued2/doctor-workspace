from typing import List


class Solution:
    @staticmethod
    def maxAscendingSum(nums: List[int]) -> int:
        # Initialize maxSum to store the maximum sum of ascending subarrays
        maxSum = 0
        # Initialize currentSum to store the current sum of the ascending subarray
        currentSum = 0
        # Initialize prevNum to negative infinity to handle the first comparison correctly
        prevNum = float('-inf')

        # Iterate through each number in the list
        for num in nums:
            # Check if the current number is greater than the previous number
            if num > prevNum:
                # If it is, add it to the current sum
                currentSum += num
            else:
                # If the current number is not greater, start a new ascending subarray
                currentSum = num
            # Update maxSum if the currentSum is greater than maxSum
            maxSum = max(maxSum, currentSum)
            # Update prevNum to the current number for the next iteration
            prevNum = num

        # Return the maximum sum found
        return maxSum


print(Solution.maxAscendingSum(nums=[12, 17, 15, 13, 10, 11, 12]))
