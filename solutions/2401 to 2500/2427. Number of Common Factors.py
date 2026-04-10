class Solution:
    @staticmethod
    def commonFactors(a: int, b: int) -> int:
        # Initialize a counter to keep track of the common factors
        count = 0

        # Check if b is a factor of a
        if a % b == 0:
            count += 1

        # Iterate through the numbers from 1 to half of the minimum of a and b
        for i in range(1, (min(a, b) // 2) + 1):
            # Check if i is a factor of both a and b
            if a % i == 0 and b % i == 0:
                count += 1

        # Return the total count of common factors
        return count


print(Solution.commonFactors(a=12, b=6))
