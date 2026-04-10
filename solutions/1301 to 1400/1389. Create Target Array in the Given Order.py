from typing import List


class Solution:
    @staticmethod
    def createTargetArray(nums: List[int], index: List[int]) -> List[int]:
        # Get the length of the nums list
        n = len(nums)

        # Initialize the result list as an empty list
        res = []

        # Loop over the range from 0 to n-1
        for i in range(n):
            # Insert the value nums[i] into the res list at the position index[i]
            res.insert(index[i], nums[i])

        # Return the final result list after all insertions are done
        return res


print(Solution.createTargetArray(nums=[0, 1, 2, 3, 4], index=[0, 1, 2, 2, 1]))
