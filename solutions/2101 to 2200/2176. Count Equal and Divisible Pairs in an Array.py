from typing import List


class Solution:
    @staticmethod
    def countPairs(nums: List[int], k: int) -> int:
        # Initialize the count of valid pairs to 0
        ans = 0

        # Iterate over all pairs (i, j) where i < j
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                # Check if the product of indices is divisible by k
                if (i * j) % k == 0:
                    # Check if the elements at indices i and j are the same
                    if nums[i] == nums[j]:
                        # Increment the count of valid pairs
                        ans += 1
        # Return the total count of valid pairs
        return ans


# Example usage:
print(Solution.countPairs(nums=[3, 1, 2, 2, 2, 1, 3], k=2))  # Adjust the example as needed
