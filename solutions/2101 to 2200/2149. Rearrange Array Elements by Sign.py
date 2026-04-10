from typing import List


class Solution:
    @staticmethod
    def rearrangeArray(nums: List[int]) -> List[int]:
        # Initialize the result list with zeros, the same length as the input list
        res = [0] * len(nums)

        # Separate the input list into positive and negative numbers
        pos, neg = [], []

        # Iterate through each number in the input list
        for i in nums:
            # Append to the neg list if the number is negative
            if i < 0:
                neg.append(i)
            else:
                # Append to the pos list if the number is positive
                pos.append(i)

        # Place positive numbers at even indices in the result list
        res[0: len(res): 2] = pos
        # Place negative numbers at odd indices in the result list
        res[1: len(res): 2] = neg

        # Return the rearranged list
        return res


print(Solution.rearrangeArray(nums=[3, 1, -2, -5, 2, -4]))
