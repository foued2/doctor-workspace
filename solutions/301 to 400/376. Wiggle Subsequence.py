from typing import List


class Solution:
    @staticmethod
    def wiggleMaxLength(nums: List[int]) -> int:
        """
        Dynamic Programming
        """
        if not nums:
            return 0

        # Initialize the two counters that represent the lengths of the longest wiggle sequences
        # ending with a rising edge (up) and with a falling edge (down),
        # starting with the first element both being 1.
        up_sequence_length = 1
        down_sequence_length = 1

        # Iterate through the array starting from the second element
        for i in range(1, len(nums)):
            # If the current element is greater than the previous one,
            # update the rising edge length (up_sequence_length)
            if nums[i] > nums[i - 1]:
                up_sequence_length = max(up_sequence_length, down_sequence_length + 1)
            # If the current element is smaller than the previous one,
            # update the falling edge length (down_sequence_length)
            elif nums[i] < nums[i - 1]:
                down_sequence_length = max(down_sequence_length, up_sequence_length + 1)

        # Return the maximum length between the two wiggle subsequences
        return max(up_sequence_length, down_sequence_length)


if __name__ == '__main__':
    # Test the solution with an example input
    print(Solution().wiggleMaxLength([1, 17, 5, 10, 13, 15, 10, 5, 16, 8]))
