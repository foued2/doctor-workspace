from typing import List


class Solution:
    @staticmethod
    def semiOrderedPermutation(nums: List[int]) -> int:
        # Initialize the variable to store the answer
        ans = 0

        # Get the length of the input list 'nums'
        n = len(nums)

        # Find the index of the smallest number (1) in the list
        start = nums.index(1)

        # Find the index of the largest number (n) in the list
        end = nums.index(n)

        # If the index of the smallest number is greater than the index of the largest number
        # It means that they are not in the correct order, so we decrement 'ans' by 1
        if start > end:
            ans -= 1

        # Add the number of moves required to bring 1 to the start and n to the end
        # This is calculated by summing the distance of 1 from the start (start)
        # and the distance of n from the end ((n - 1) - end)
        ans += start + (n - 1) - end

        # Return the calculated answer
        return ans


print(Solution.semiOrderedPermutation(nums=[2, 4, 1, 3]))
