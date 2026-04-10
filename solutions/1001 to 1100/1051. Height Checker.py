from typing import List


class Solution:
    @staticmethod
    def heightChecker(heights: List[int]) -> int:
        """
        Counting sort
        """
        # Find the maximum height to size the counting sort array appropriately
        max_height = max(heights)

        # Initialize the counting sort array
        counting_sort = [0] * (max_height + 1)

        # Populate the counting sort array
        for height in heights:
            counting_sort[height] += 1

        # Initialize the mismatch counter
        mismatch_count = 0
        current_height = 0

        # Iterate over the original heights list to compare with the expected heights
        for i in range(len(heights)):
            # Find the next height that should appear in the sorted order
            while counting_sort[current_height] == 0:
                current_height += 1

            # If the current height in the original list does not match the expected height
            if heights[i] != current_height:
                mismatch_count += 1

            # Decrease the count for the current height
            counting_sort[current_height] -= 1

        return mismatch_count


# Example usage:
heights = [1, 1, 4, 2, 1, 3]
print(Solution.heightChecker(heights))  # Output should be 3
