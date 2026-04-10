from typing import List


class Solution:
    @staticmethod
    def prefixesDivBy5(nums: List[int]) -> List[bool]:
        """
        Dynamic Programming
        """
        # Initialize an empty list to store the results
        res = []

        # Determine the length of the input list
        n = len(nums)

        # Initialize a DP array to store the decimal values of the prefixes
        dp = [0] * n

        # The first element in dp is just the first element of nums
        dp[0] = nums[0]

        # Check if the first prefix (first element) is divisible by 5
        if dp[0] % 5 == 0:
            res.append(True)
        else:
            res.append(False)

        # Iterate through the remaining elements in the input list
        for i in range(1, n):
            # Calculate the decimal value of the current prefix based on the previous prefix
            # Shift the previous prefix value left (multiply by 2) and add the current bit
            dp[i] = dp[i - 1] * 2 + nums[i]

            # Check if the current decimal value is divisible by 5
            if dp[i] % 5 == 0:
                res.append(True)
            else:
                res.append(False)

        # Return the list containing boolean values for each prefix
        return res


# Example usage
if __name__ == '__main__':
    print(Solution.prefixesDivBy5(nums=[0, 1, 1, 1, 1, 1]))


class Solution:
    @staticmethod
    def prefixesDivBy5(nums: List[int]) -> List[bool]:
        """
        Bit Manipulation
        """
        # Initialize a variable 'c' to store the current prefix value in a modulo 5 form
        c = 0

        # Initialize an empty list to store the boolean results
        res = []

        # Iterate through each binary digit in the input list
        for n in nums:
            # Update the prefix value 'c' by shifting it left (multiplying by 2),
            # adding the current bit 'n',
            # and then taking the result modulo 5 to keep it manageable.
            c = (c * 2 + n) % 5

            # Check if the current prefix value 'c' is divisible by 5 (i.e., if it is 0)
            res.append(c == 0)

        # Return the list containing boolean values for each prefix
        return res


# Example usage
if __name__ == '__main__':
    print(Solution.prefixesDivBy5(nums=[0, 1, 1, 1, 1, 1]))