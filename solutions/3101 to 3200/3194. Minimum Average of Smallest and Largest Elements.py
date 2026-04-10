from typing import List


class Solution:
    @staticmethod
    def minimumAverage(nums: List[int]) -> float:
        averages = []  # List to store the averages of pairs
        n = len(nums)  # Length of the input list
        nums.sort()  # Sort the list in ascending order
        for i in range(n):
            # Calculate the average of the ith smallest and ith largest elements
            averages.append((nums[i] + nums[n - i - 1]) / 2)
        # Return the minimum average from the list of averages
        return min(averages)


if __name__ == '__main__':
    # Testing the static method with a sample list of numbers
    print(Solution().minimumAverage(nums=[7, 8, 3, 4, 15, 13, 4, 1]))