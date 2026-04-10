from typing import List


class Solution:
    @staticmethod
    def repeatedNTimes(nums: List[int]) -> int:
        # Calculate the value of 'n', which is half the length of the list
        n = len(nums) // 2

        # Initialize an empty dictionary to store the count of each element
        table = {}

        # Iterate through the list to count occurrences of each element
        for num in nums:
            table[num] = table.get(num, 0) + 1

            # If the count of the current element reaches 'n', return the element
            if table[num] == n:
                return num


if __name__ == '__main__':
    print(Solution.repeatedNTimes([5, 1, 5, 2, 5, 3, 5, 4]))
