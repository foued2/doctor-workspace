from typing import List
from collections import defaultdict
import math


class Solution:
    @staticmethod
    def prime_factors(n: int) -> List[int]:
        factors = defaultdict(int)
        # Check for number of 2s
        while n % 2 == 0:
            factors[2] += 1
            n //= 2
        # Check for odd factors
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            while n % i == 0:
                factors[i] += 1
                n //= i
        # If n is still a prime number greater than 2
        if n > 2:
            factors[n] += 1
        return factors

    @staticmethod
    def kthFactor(n: int, k: int) -> int:
        """
        Prime Factorization, Number Theory
        """
        # List to store the factors
        factors = []

        # Iterate over all possible factors from 1 to sqrt(n)
        for i in range(1, int(n ** 0.5) + 1):
            if n % i == 0:
                # If i is a factor, add it to the list
                factors.append(i)
                # If n // i is different from i, add n // i as well
                if i != n // i:
                    factors.append(n // i)

        # Sort the list of factors
        factors.sort()

        # Check if k-th factor exists
        if k <= len(factors):
            return factors[k - 1]
        else:
            return -1


print(Solution.kthFactor(n=100, k=6))
