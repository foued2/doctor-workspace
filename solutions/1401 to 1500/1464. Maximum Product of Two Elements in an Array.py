from typing import List  # Importing List type from typing module


class Solution:
    @staticmethod
    def maxProduct(nums: List[int]) -> int:
        # Sorting the input list in ascending order
        nums = sorted(nums)

        # Calculating the maximum product of two distinct elements
        # Subtracting 1 from each element to get the reduced value
        return (nums[-1] - 1) * (nums[-2] - 1)


if __name__ == '__main__':
    print(Solution.maxProduct(nums=[1, 5, 4, 5]))


class Solution:
    @staticmethod
    def maxProduct(nums: List[int]) -> int:
        # Initialize the two largest numbers
        first_max, second_max = 0, 0

        # Find the two largest numbers in the array
        for num in nums:
            if num > first_max:
                second_max = first_max
                first_max = num
            elif num > second_max:
                second_max = num

        # Compute and return the product of (first_max - 1) and (second_max - 1)
        return (first_max - 1) * (second_max - 1)


# Example usage
if __name__ == '__main__':
    print(Solution.maxProduct([3, 4, 5, 2]))  # Output: 12