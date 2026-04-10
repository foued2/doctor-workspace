from typing import List


class Solution:
    @staticmethod
    def maxProductDifference(nums: List[int]) -> int:
        """
        Greedy
        """
        # Find the maximum and second maximum numbers in the list
        m1 = max(nums)
        nums.remove(m1)
        m2 = max(nums)

        # Find the minimum and second minimum numbers in the list
        m3 = min(nums)
        nums.remove(m3)
        m4 = min(nums)

        # Calculate the final result by subtracting the product of two minimum numbers from the product of two
        # maximum numbers
        final = (m1 * m2) - (m3 * m4)

        # Return the final result
        return final


if __name__ == '__main__':
    print(Solution.maxProductDifference(nums=[4, 2, 5, 9, 7, 4, 8]))
