from typing import List


class Solution:
    @staticmethod
    def check(nums: List[int]) -> bool:
        # Get the length of the nums list
        n = len(nums)

        # Create a sorted copy of nums
        copy = sorted(nums)

        # Iterate through all possible rotations
        for x in range(n):
            # Use any() to check if there is any mismatch in the current rotation
            if all(nums[i] == copy[(i + x) % n] for i in range(n)):
                # If no mismatches are found, return True
                return True

        # If no rotation matches, return False
        return False


print(Solution.check(nums=[3, 4, 5, 1, 2]))
