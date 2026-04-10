from typing import List


class Solution:
    @staticmethod
    def findIndices(nums: List[int], indexDifference: int, valueDifference: int) -> List[int]:
        n = len(nums)
        answer = [-1, -1]  # Initialize the answer with default values

        # Iterate through the list to find pairs of indices
        for i in range(n - indexDifference):
            for j in range(i + indexDifference, n):
                # Check if the absolute difference between the values at indices i and j is greater than or equal to
                # 'valueDifference'
                if abs(nums[i] - nums[j]) >= valueDifference:
                    return [i, j]  # Return the indices if the condition is met

        # If no such pair is found, return the default answer
        return answer


if __name__ == '__main__':
    print(Solution.findIndices(nums=[5, 1, 4, 1], indexDifference=2, valueDifference=4))
