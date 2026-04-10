from typing import List


class Solution:
    @staticmethod
    def divideArray(nums: List[int]) -> bool:
        """
        Bit manipulation, xor
        """
        # Sort the array in non-decreasing order
        nums.sort()

        # Get the length of the array
        n = len(nums)

        # Iterate over the array in steps of 2
        for i in range(0, n - 1, 2):
            # Calculate the XOR of the current pair of elements
            xor = nums[i] ^ nums[i + 1]

            # If the XOR of the pair is not zero, it means there's no pair that can make the XOR zero,
            # hence return False
            if xor != 0:
                return False

        # If all pairs have XOR equal to zero, return True
        return True


print(Solution.divideArray([4, 1, 2, 1, 2]))  # Output: 4
