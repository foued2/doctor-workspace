from typing import List


class Solution:
    @staticmethod
    def returnToBoundaryCount(nums: List[int]) -> int:
        """
        Prefix Sum
        """
        # Initialize variables to keep track of the boundary count and cumulative sum
        boundary = 0
        steps = 0
        # Iterate through each step in the list
        for step in nums:
            # Update the cumulative sum
            steps += step
            # Check if the cumulative sum returns to zero
            if steps == 0:
                # If it does, increment the boundary count
                boundary += 1

        # Return the total boundary count
        return boundary


if __name__ == '__main__':
    # Example usage
    print(Solution.returnToBoundaryCount([3, 2, -3, -4]))
