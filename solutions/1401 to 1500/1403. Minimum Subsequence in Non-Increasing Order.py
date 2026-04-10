from typing import List


class Solution:
    @staticmethod
    def minSubsequence(nums: List[int]) -> List[int]:
        # Initialize an empty list to store the result subsequence
        res = []

        # Initialize max_sum to store the sum of the current subsequence
        max_sum = 0

        # Calculate the sum of all elements in the input list
        sum_nums = sum(nums)

        # Sort the input list in descending order to try larger numbers first
        nums = sorted(nums, reverse=True)

        # Iterate through each number in the sorted list
        for num in nums:
            # Add the current number to max_sum
            max_sum += num

            # Append the current number to the result subsequence
            res.append(num)

            # Check if the sum of the current subsequence is greater than the sum of the remaining elements
            if max_sum > (sum_nums - max_sum):
                # If true, break the loop since we found the minimum subsequence
                break

        # Return the result subsequence
        return res


print(Solution.minSubsequence(nums=[4, 3, 10, 9, 8]))
