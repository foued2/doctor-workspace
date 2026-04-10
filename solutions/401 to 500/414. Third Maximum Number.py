from typing import List


class Solution:
    @staticmethod
    def thirdMax(nums: List[int]) -> int:
        # Dictionary to store the frequency of each number
        num_frequency = {}

        # Populate the dictionary with the frequency count for each number in the list
        for num in nums:
            if num in num_frequency:
                num_frequency[num] += 1
            else:
                num_frequency[num] = 1

        # Extract the unique numbers and sort them
        nums = sorted(num_frequency.keys())

        # If there are less than 3 unique numbers, return the maximum
        if len(nums) < 3:
            return max(nums)
        else:
            # Otherwise, return the third maximum number
            return nums[-3]


if __name__ == "__main__":
    print(Solution.thirdMax([2, 2, 3, 1]))


class Solution:
    @staticmethod
    def thirdMax(nums: List[int]) -> int:
        # Converting the list to a set to remove duplicates
        nums = set(nums)

        # If there are less than three unique numbers, return the maximum
        if len(nums) < 3:
            return max(nums)

        # Remove the first maximum
        nums.remove(max(nums))

        # Remove the second maximum
        nums.remove(max(nums))

        # Now the maximum number left is the third maximum
        return max(nums)