from typing import List


class Solution:
    @staticmethod
    def uniqueOccurrences(arr: List[int]) -> bool:
        # Create a dictionary to store the frequency of each number
        frequency_table = {}

        # Iterate over the numbers in the input list
        for num in arr:
            # Update the frequency of the current number in the dictionary
            frequency_table[num] = frequency_table.get(num, 0) + 1

        # Check if the number of unique frequencies is equal to the number of unique numbers
        if len(set(frequency_table.values())) != len(frequency_table.keys()):
            return False  # If not, return False

        # If all frequencies are unique, return True
        return True


print(Solution.uniqueOccurrences(arr=[-3, 0, 1, -3, 1, 1, 1, -3, 10, 0]))
