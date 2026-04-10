from typing import List


class Solution:
    @staticmethod
    def shuffle(nums: List[int], n: int) -> List[int]:
        # Initialize an empty list to store the shuffled numbers
        new_nums = []

        # Iterate over the first 'n' elements of the input list
        for i in range(n):
            # Append the current element at index 'i' to the new list
            new_nums.append(nums[i])
            # Append the corresponding element at index 'i+n' to the new list
            new_nums.append(nums[i + n])

        # Return the shuffled list
        return new_nums


if __name__ == '__main__':
    print(Solution.shuffle(nums=[1, 2, 3, 4, 4, 3, 2, 1], n=3))
