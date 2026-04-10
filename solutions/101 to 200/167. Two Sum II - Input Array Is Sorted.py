from typing import List


class Solution:
    @staticmethod
    def twoSum(numbers: List[int], target: int) -> List[int]:
        # Initialize two pointers, left and right, at the start and end of the array
        left, right = 0, len(numbers) - 1

        # Iterate until left pointer is less than right pointer
        while left < right:
            # Calculate the sum of elements at left and right pointers
            curr_sum = numbers[left] + numbers[right]

            # Check if the sum equals the target
            if curr_sum == target:
                # Return the indices (1-indexed) of the elements
                return [left + 1, right + 1]
            # If the sum is less than the target, move the left pointer to the right
            elif curr_sum < target:
                left += 1
            # If the sum is greater than the target, move the right pointer to the left
            else:
                right -= 1

        # If no pair is found, return an empty list
        return []


# Test the twoSum method
print(Solution.twoSum(numbers=[-1, 0], target=-1))
