from collections import Counter
from typing import List


class Solution:
    @staticmethod
    def countKDifference(nums: List[int], k: int) -> int:
        # Initialize a variable to keep track of the number of valid pairs
        ans = 0

        # Create a Counter (dictionary) to count the occurrences of each number in the list
        table = Counter(nums)

        # Iterate through the unique numbers in the Counter
        for num in table:
            # Check if the number num + k exists in the Counter
            if num + k in table:
                # If it exists, add the product of their counts to ans
                ans += table[num] * table[num + k]
            # Check if the number num - k exists in the Counter
            if num - k in table:
                # If it exists, add the product of their counts to ans
                ans += table[num] * table[num - k]

        # Since each pair is counted twice (num, num + k) and (num + k, num), divide the result by 2
        return ans // 2


print(Solution.countKDifference(nums=[1, 2, 2, 1], k=1))
