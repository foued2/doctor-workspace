from typing import List


class Solution:
    @staticmethod
    def countHillValley(nums: List[int]) -> int:
        # Remove consecutive duplicates
        # We do this to ensure we don't falsely identify flat sections
        # between hills and valleys.
        filtered_nums = [nums[i] for i in range(len(nums)) if i == 0 or nums[i] != nums[i - 1]]

        # Initialize the count of hills and valleys
        count = 0

        # Loop through the filtered list starting from the second element
        # and ending at the second to last element.
        for i in range(1, len(filtered_nums) - 1):
            # Check if the current element is a hill.
            # A hill is formed if nums[i] is greater than both its neighbors.
            if filtered_nums[i] > filtered_nums[i - 1] and filtered_nums[i] > filtered_nums[i + 1]:
                count += 1
            # Check if the current element is a valley.
            # A valley is formed if nums[i] is less than both its neighbors.
            elif filtered_nums[i] < filtered_nums[i - 1] and filtered_nums[i] < filtered_nums[i + 1]:
                count += 1

        # Return the total count of hills and valleys.
        return count


if __name__ == '__main__':
    # Example usage:
    # The array [2, 4, 1, 1, 6, 5] has the elements (4, 1) forming a hill and valley respectively.
    # After filtering duplicates: [2, 4, 1, 6, 5]
    # 4 is a hill (greater than 2 and 1)
    # 1 is a valley (less than 4 and 6)
    # 6 is a hill (greater than 1 and 5)
    # Expected output is 3
    print(Solution.countHillValley([2, 4, 1, 1, 6, 5]))  # Output should be 3ion.countHillValley([2, 4, 1, 1, 6, 5]))