from collections import Counter
from typing import List


class Solution:
    @staticmethod
    def mostFrequentEven(nums: List[int]) -> int:
        # Create a Counter object to count occurrences of each number
        table = Counter(nums)

        # Initialize variables to track the maximum frequency of even numbers and the corresponding number
        max_even = 0
        ans = -1

        # Iterate over each unique number and its count in the Counter object
        for key, value in table.items():
            even = 0
            # Check if the current number is even
            if key % 2 == 0:
                even = value
            # Update the maximum frequency and corresponding number if a new maximum is found
            if even > max_even:
                max_even = even
                ans = key
            # If the frequency is equal to the maximum, choose the smaller number
            if even == max_even:
                ans = min(ans, key)

        # Return the most frequently occurring even number
        return ans


print(Solution.mostFrequentEven(nums=[4, 4, 4, 9, 2, 4]))

print(Solution.mostFrequentEven(nums=[29, 47, 21, 41, 13, 37, 25, 7]))
