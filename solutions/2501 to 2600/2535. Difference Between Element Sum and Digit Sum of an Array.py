from typing import List


class Solution:
    @staticmethod
    def differenceOfSum(nums: List[int]) -> int:
        # Calculate the sum of all elements in the list
        element_sum = sum(nums)

        # Initialize a variable to store the sum of digits of all numbers in the list
        digit_sum = 0

        # Iterate through each number in the list
        for num in nums:
            # Extract the digits of the number and add them to the digit_sum
            while num > 0:
                digit_sum += num % 10  # Add the last digit of num to digit_sum
                num //= 10  # Remove the last digit from num

        # Calculate the absolute difference between the element sum and the digit sum
        difference = abs(element_sum - digit_sum)

        # Return the absolute difference
        return difference


print(Solution.differenceOfSum(nums=[1, 15, 6, 3]))
