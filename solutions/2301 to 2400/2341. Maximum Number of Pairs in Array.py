from typing import List


class Solution:
    @staticmethod
    def numberOfPairs(nums: List[int]) -> List[int]:
        """
        Hash map, Reverse hashing
        """
        # Initialize a dictionary to store the count of each number
        count_map = {}
        # Initialize a variable to count pairs
        pair_count = 0

        # Iterate through each number in the input list
        for num in nums:
            # Check if the number is not in the count_map
            if num not in count_map:
                # If the number is not in the count_map, add it with a count of 1
                count_map[num] = 1
            else:
                # If the number is already in the count_map, remove it and increment pair_count
                del count_map[num]
                pair_count += 1

        # Return a tuple containing the number of pairs and the count of remaining numbers in count_map
        return [pair_count, len(count_map)]


print(Solution.numberOfPairs(nums=[1, 3, 2, 1, 3, 2, 2]))
