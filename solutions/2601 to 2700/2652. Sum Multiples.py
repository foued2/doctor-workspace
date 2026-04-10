from math import floor


class Solution:
    @staticmethod
    def sumOfMultiples(n: int) -> int:
        # Using gaussian summation formula: 1 + 2 + 3 + ... + n = n * (n+1) / 2
        # Sum from 1 to n divisible by 3: 3 * (1 + 2 + ... + n/3)
        # In general:
        # Sum from 1 to n divisible by k: k * ( 1 + 2 + .. + k/3)

        def sum_k(k):
            # Calculate the number of multiples of k up to n
            upper = floor(n / k)
            # Calculate the sum of multiples of k using the gaussian summation formula
            return k * (upper * (upper + 1) / 2)

        # Inclusion-exclusion principle for overcounting
        return int(sum_k(3) + sum_k(5) + sum_k(7) - sum_k(3 * 5) - sum_k(3 * 7) - sum_k(5 * 7) + sum_k(3 * 5 * 7))


print(Solution.sumOfMultiples(15))
