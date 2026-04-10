import collections
from typing import List


class Solution:
    @staticmethod
    def frequencySort(nums: List[int]) -> List[int]:
        result = []

        # Create a counter to count the frequency of each number in the nums list
        counter = collections.Counter(nums)

        # Initialize a dictionary to reverse the mapping of counter
        reverse = {}

        # Iterate over the counter dictionary
        for key, value in counter.items():
            # If the frequency (value) is not already a key in reverse, create a new list
            if value not in reverse:
                reverse[value] = [key]
            else:
                reverse[value].append(key)

        # Sort the keys of reverse dictionary (which are frequencies) in ascending order
        for frequency in sorted(reverse.keys()):
            # For each frequency, sort the corresponding numbers in descending order and extend the result
            for num in sorted(reverse[frequency], reverse=True):
                # Append the number frequency times to the result list
                result.extend([num] * frequency)

        return result


if __name__ == '__main__':
    # Example usage of the frequencySort method
    print(Solution().frequencySort([1, 1, 2, 2, 2, 3, 3]))


class Solution:
    @staticmethod
    def frequencySort(nums: List[int]) -> List[int]:
        """
        Custom sorting key function
        """
        # Count the frequency of each number in the input list nums
        counts = collections.Counter(nums)

        # Sort nums using a custom sorting key:
        # 1. Sort by the frequency of each number (counts[x])
        # 2. For numbers with the same frequency, sort by the number itself in descending order (-x)
        sorted_nums = sorted(nums, key=lambda x: (counts[x], -x))

        # Return the sorted list
        return sorted_nums


if __name__ == '__main__':
    # Example usage of the frequencySort method
    print(Solution().frequencySort([1, 1, 2, 2, 2, 3, 3]))