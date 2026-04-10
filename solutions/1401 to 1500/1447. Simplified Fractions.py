from typing import List
from collections import deque
from math import gcd


class Solution:
    @staticmethod
    def simplifiedFractions(n: int) -> List[str]:
        # Initialize a deque to store simplified fractions
        simplified_fractions = deque()

        # Loop through each numerator from 1 to n-1
        for numerator in range(1, n):
            # Loop through each denominator from numerator+1 to n
            for denominator in range(numerator + 1, n + 1):
                # Check if the numerator and denominator are coprime
                if gcd(numerator, denominator) == 1:
                    # If they are coprime, append the fraction to the deque
                    simplified_fractions.append(f'{numerator}/{denominator}')

        # Convert the deque to a list and return it
        return list(simplified_fractions)


# Example usage:
solution = Solution()
result = solution.simplifiedFractions(5)
print(result)  # Output: ['1/2', '1/3', '2/3', '1/4', '3/4', '1/5', '2/5', '3/5', '4/5']
