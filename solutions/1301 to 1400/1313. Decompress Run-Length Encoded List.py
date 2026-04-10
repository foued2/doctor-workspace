from typing import List


class Solution:
    @staticmethod
    def decompressRLElist(nums: List[int]) -> List[int]:
        # Initialize an empty list to store the decompressed result.
        res = []
        # Get the length of the input list.
        n = len(nums)
        # Iterate over the input list in steps of 2.
        for i in range(0, n, 2):
            # nums[i] is the frequency, nums[i + 1] is the value.
            # extend the result list by repeating the value 'nums[i + 1]' for 'nums[i]' times.
            res.extend([nums[i + 1]] * nums[i])
        # Return the decompressed list.
        return res


print(Solution.decompressRLElist(nums=[1, 1, 2, 3]))
