from typing import List
import math


class Solution:
    @staticmethod
    def countBeautifulPairs(nums: List[int]) -> int:
        def areCoprime(a, b):
            # Calculate the greatest common divisor (GCD) of the two integers
            gcd = math.gcd(a, b)

            # Check if the GCD is 1
            if gcd == 1:
                # If the GCD is 1, the integers are coprime
                return True
            else:
                # If the GCD is not 1, the integers are not coprime
                return False

        # Initialize a counter for the number of beautiful pairs
        ans = 0

        # Get the length of the input list
        n = len(nums)

        # Iterate through each pair of elements in the list
        for i in range(n):
            for j in range(i + 1, n):
                # Get the first digit of the current element
                first = int(str(nums[i])[0])

                # Get the last digit of the next element
                last = int(str(nums[j])[-1])

                # Check if the first and last digits are coprime
                if areCoprime(first, last):
                    # If they are coprime, increment the counter
                    ans += 1

        # Return the total count of beautiful pairs
        return ans


# Example usage:
# Create an instance of the Solution class
solution = Solution()

# Define a list of numbers
nums = [23, 35, 67, 89, 12, 45]

# Call the countBeautifulPairs method and print the result
# This should return the count of


print(Solution.countBeautifulPairs(nums=[11, 21, 12]))
