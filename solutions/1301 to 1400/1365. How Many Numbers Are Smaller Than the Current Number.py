from collections import defaultdict
from typing import List


class Solution:
    @staticmethod
    def smallerNumbersThanCurrent(nums: List[int]) -> List[int]:
        """
        Hash Table
        """
        # Initialize a defaultdict to store the counts of smaller numbers for each element
        table = defaultdict(int)

        # Count the frequency of each number in nums
        for num in nums:
            table[num] += 1

        # Create a sorted list of unique numbers in nums
        unique_nums = sorted(set(nums))

        # Calculate the number of smaller elements for each unique number
        smaller_counts = {}
        smaller_sum = 0
        for num in unique_nums:
            smaller_counts[num] = smaller_sum
            smaller_sum += table[num]

        # Return the counts of smaller numbers for each element in nums
        return [smaller_counts[num] for num in nums]


if __name__ == '__main__':
    print(Solution.smallerNumbersThanCurrent([8, 1, 2, 2, 3]))
