from typing import List


class Solution:
    @staticmethod
    def sumOfUnique(nums: List[int]) -> int:
        # Initialize an empty dictionary to store the frequency of each number.
        d = {}

        # Iterate through the list of numbers.
        for i in range(len(nums)):
            # Check if the current number is already in the dictionary.
            if nums[i] not in d:
                # If the number is not in the dictionary, add it with a frequency of 1.
                d[nums[i]] = 1
            else:
                # If the number is already in the dictionary, increment its frequency by 1.
                d[nums[i]] += 1

        # Initialize a variable to store the sum of unique elements.
        ans = 0

        # Iterate through the keys (unique elements) in the dictionary.
        for i in d.keys():
            # Check if the frequency of the current element is 1, indicating it is unique.
            if d[i] == 1:
                # If the element is unique, add it to the sum.
                ans += i

        # Return the sum of unique elements.
        return ans


print(Solution.sumOfUnique(nums=[1, 1, 1, 1, 2, 1]))
