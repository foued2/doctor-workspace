from typing import List


class Solution:
    @staticmethod
    def maximumTripletValue(nums: List[int]) -> int:
        # Initialize the answer to store the maximum triplet value
        max_triplet_value = 0
        # Initialize the maximum difference between any two numbers
        max_difference = 0
        # Initialize the maximum number encountered so far
        max_number = 0

        # Iterate through each number in the list
        for num in nums:
            # Update the maximum triplet value by considering the current product of max_difference and the current
            # number
            max_triplet_value = max(max_triplet_value, max_difference * num)
            # Update the maximum difference by considering the current difference between max_number and the current
            # number
            max_difference = max(max_difference, max_number - num)
            # Update the maximum number encountered so far
            max_number = max(max_number, num)

        # Return the maximum triplet value found
        return max_triplet_value


# Example usage:
solution = Solution()
result = solution.maximumTripletValue([1, 5, 3, 2, 4])
print(result)  # Example output: 12 (which could be from (5 - 1) * 4)


class Solution:
    @staticmethod
    def maximumTripletValue(nums: List[int]) -> int:
        # Initialize the answer to store the maximum triplet value
        max_triplet_value = 0

        # Iterate through each element in nums except the first and last
        for i in range(1, len(nums) - 1):
            # Find the maximum value to the left of the current element
            left_max = max(nums[:i])
            # The current element is considered as the middle element
            middle = nums[i]
            # Find the maximum value to the right of the current element
            right_max = max(nums[i + 1:])
            # Calculate the triplet value (left - middle) * right
            current_triplet_value = (left_max - middle) * right_max

            # Update the maximum triplet value if the current one is greater
            if current_triplet_value > max_triplet_value:
                max_triplet_value = current_triplet_value

        # Return the maximum triplet value found
        return max_triplet_value


# Example usage:
solution = Solution()
result = solution.maximumTripletValue([1, 5, 3, 2, 4])
print(result)  # Example output: 12 (which could be from (5 - 1) * 4)
