from typing import List


class Solution:
    @staticmethod
    def kLengthApart(nums: List[int], k: int) -> bool:
        # Initialize a variable to keep track of the current distance between 1s
        current_distance = k

        # Iterate over the elements in the nums list
        for num in nums:
            # If the current element is 1
            if num == 1:
                # Check if the current distance between 1s is less than k
                if current_distance < k:
                    return False  # If so, return False
                current_distance = 0  # Reset the current distance
            else:
                # If the current element is 0, increment the current distance
                current_distance += 1

        # If all 1s are at least k places apart, return True
        return True


print(Solution.kLengthApart(nums=[1, 0, 0, 0, 1, 0, 0, 1], k=2))
