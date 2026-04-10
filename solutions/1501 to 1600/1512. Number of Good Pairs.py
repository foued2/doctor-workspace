from typing import List


class Solution:
    @staticmethod
    def numIdenticalPairs(nums: List[int]) -> int:
        ans = 0  # Initialize a variable to store the count of pairs
        table = {}  # Initialize an empty dictionary to store the count of each element

        # Count the occurrences of each element in the list
        for num in nums:
            table[num] = table.get(num, 0) + 1

        # Iterate through the counts of elements in the dictionary
        for n in table.values():
            # Calculate the number of pairs using the combination formula nC2
            ans += (n * (n - 1)) // 2

        # Return the total count of pairs
        return ans


if __name__ == '__main__':
    print(Solution.numIdenticalPairs([1, 2, 3, 1, 1, 3]))
