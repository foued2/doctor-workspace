class Solution:
    @staticmethod
    def alternateDigitSum(n: int) -> int:
        # Convert the integer n to a list of digits
        nums = [int(i) for i in str(n)]

        # Initialize a variable to store the alternate digit sum
        ans = 0

        # Initialize a variable to control the sign of each digit
        sign = 1

        # Iterate through each digit in the list of digits
        for num in nums:
            # Add the current digit to the alternate digit sum with the appropriate sign
            ans += sign * num

            # Toggle the sign for the next digit
            sign *= -1

        # Return the alternate digit sum
        return ans


print(Solution.alternateDigitSum(n=131))
