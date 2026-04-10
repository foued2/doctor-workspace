from typing import List


class Solution:
    @staticmethod
    def maxFrequencyElements(nums: List[int]) -> int:
        # Initialize the answer variable to store the sum of frequencies of the elements with max frequency
        ans = 0
        # Initialize a dictionary to store the frequency of each element
        table = {}

        # Iterate over each element in the input list nums
        for num in nums:
            # For each element, update its frequency in the dictionary
            # If the element is not in the dictionary, get() returns 0 and we add 1
            # If the element is already in the dictionary, increment its count by 1
            table[num] = table.get(num, 0) + 1

        # Iterate over the frequency values in the dictionary
        for value in table.values():
            # Check if the current frequency value is equal to the maximum frequency in the dictionary
            if value == max(table.values()):
                # If true, add the frequency value to the answer
                ans += value

        # Return the sum of frequencies of elements with the maximum frequency
        return ans


# Example usage
solution = Solution()
print(solution.maxFrequencyElements([1, 2, 2, 3, 3, 3, 4, 4, 4, 4]))  # Output: 4
