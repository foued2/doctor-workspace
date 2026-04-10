from typing import List


class Solution:
    @staticmethod
    def largestNumber(nums: List[int]) -> str:
        # Convert all integers in the list to strings for easy comparison
        nums = list(map(str, nums))

        # Sort the string numbers using a custom key.
        # The key for sorting is each string number doubled and compared.
        # This trick ensures the highest possible combination when numbers are concatenated.
        nums.sort(key=lambda x: x * 2, reverse=True)

        # Join the sorted numbers into a single string to form the largest number.
        # Handle the edge case where the largest number is '0'.
        return ''.join(nums)


if __name__ == '__main__':
    # Example usage: prints the largest number that can be formed by concatenating [3, 30, 34, 5, 9]
    print(Solution().largestNumber([3, 30, 34, 5, 9]))