from typing import List
from collections import defaultdict
from heapq import heappush, heappushpop


class Solution:
    @staticmethod
    def maximumSum(nums: List[int]) -> int:
        # Initialize the answer to -1 (if no valid pairs are found)
        ans = -1
        # Use defaultdict to store the two largest numbers for each digit sum
        table = defaultdict(list)

        # Process each number in the input list
        for num in nums:
            # Calculate the sum of the digits of the number
            sum_num = sum(int(digit) for digit in str(num))

            # Add the number to the list corresponding to its digit sum
            table[sum_num].append(num)
            # Ensure the list contains at most two largest numbers
            if len(table[sum_num]) > 2:
                # Sort and keep the two largest numbers
                table[sum_num] = sorted(table[sum_num], reverse=True)[:2]

        # Iterate over the values in the table to find the maximum sum of pairs
        for value in table.values():
            # Only consider if there are exactly two numbers for a digit sum
            if len(value) == 2:
                # Calculate the sum of the two numbers
                curr_sum = sum(value)
                # Update the answer if the current sum is greater
                ans = max(ans, curr_sum)

        # Return the final answer
        return ans


# Test case
nums = [51, 71, 17, 42]

# Create an instance of Solution and test the method
solution = Solution()
output = solution.maximumSum(nums)
print(output)  # Expected: 93 (51 + 42 with digit sum 6)

print(Solution.maximumSum(nums=[9, 18, 43, 36, 13, 7]))


class Solution:
    @staticmethod
    def maximumSum(nums: List[int]) -> int:
        # Initialize a dictionary where the key is the digit sum, and the value is a list (min-heap) of numbers
        dig_sum_table = defaultdict(list)

        # Iterate over each number in the input list
        for n in nums:
            # Calculate the digit sum of the current number
            d_sum = 0
            curr = n
            while curr:
                d_sum += curr % 10  # Add the last digit to the sum
                curr //= 10  # Remove the last digit

            # If the heap for this digit sum has less than 2 elements, add the number
            if len(dig_sum_table[d_sum]) < 2:
                heappush(dig_sum_table[d_sum], n)
            # If the heap already has 2 elements and the current number is greater than the smallest element, replace it
            elif n > dig_sum_table[d_sum][0]:
                heappushpop(dig_sum_table[d_sum], n)

        # Initialize the result to -1, to indicate no valid pairs were found
        res = -1

        # Iterate over the digit sum table
        for n in dig_sum_table:
            # If there are exactly 2 numbers with the same digit sum, consider their sum
            if len(dig_sum_table[n]) == 2:
                res = max(res, sum(dig_sum_table[n]))  # Update the result with the maximum sum found

        return res  # Return the final result


# Example usage:
sol = Solution()
print(sol.maximumSum([51, 71, 17, 42]))  # Output should be the maximum sum of two numbers with the same digit sum
