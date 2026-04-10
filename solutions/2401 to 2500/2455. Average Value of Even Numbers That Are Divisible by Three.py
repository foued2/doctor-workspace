from typing import List


class Solution:
    @staticmethod
    def averageValue(nums: List[int]) -> int:
        # Initialize variables to store the sum of numbers divisible by 6 and the count of such numbers
        res = 0
        count = 0

        # Iterate through the list of numbers
        for num in nums:
            # Check if the current number is divisible by 6
            if num % 6 == 0:
                # If it is, add it to the sum and increment the count
                res += num
                count += 1

        # Check if there are numbers divisible by 6 in the list
        if count != 0:
            # If there are, return the integer division of the sum by the count
            return res // count
        else:
            # If there are no numbers divisible by 6, return 0
            return 0


if __name__ == '__main__':
    print(Solution.averageValue(nums=[1, 3, 6, 10, 12, 15]))
