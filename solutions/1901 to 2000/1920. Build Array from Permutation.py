from typing import List


class Solution:
    @staticmethod
    def buildArray(nums: List[int]) -> List[int]:
        n = len(nums)
        ans = []  # Initialize an empty list to store the result

        # Iterate through the indices of the input list 'nums'
        for i in range(n):
            # Append the value at the index specified by 'nums[i]' to the result list
            ans.append(nums[nums[i]])

        # Return the generated list
        return ans


if __name__ == '__main__':
    print(Solution.buildArray(nums=[0, 2, 1, 5, 3, 4]))
