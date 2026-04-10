from typing import List


class Solution:
    @staticmethod
    def findNumbers(nums: List[int]) -> int:
        # Initialize a variable to count the numbers with an even number of digits
        even = 0

        # Iterate through each number in the list
        for digit in nums:
            # Initialize a variable to count the number of digits in the current number
            count = 0

            # Count the number of digits in the current number using integer division
            while digit > 0:
                # Remove the last digit from the number
                digit //= 10
                # Increment the count of digits
                count += 1

            # Check if the count of digits is even
            if count % 2 == 0:
                # If the count of digits is even, increment the count of even numbers
                even += 1

        # Return the count of numbers with an even number of digits
        return even


if __name__ == '__main__':
    print(Solution.findNumbers(nums=[555, 901, 482, 1771]))
