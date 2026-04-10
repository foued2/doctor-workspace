from typing import List


class Solution:
    @staticmethod
    def leftRightDifference(nums: List[int]) -> List[int]:
        # Initialize variables to store the sum of elements to the left and right
        leftSum, rightSum = 0, sum(nums)
        # Initialize an empty list to store the results
        result = []

        # Iterate through each element in the list
        for num in nums:
            # Subtract the current element from the rightSum
            rightSum -= num
            # Calculate the absolute difference between leftSum and rightSum
            # and append it to the result list
            result.append(abs(leftSum - rightSum))
            # Add the current element to the leftSum
            leftSum += num

        # Return the list containing the absolute differences
        return result


print(Solution.leftRightDifference(nums=[10, 4, 8, 3]))
