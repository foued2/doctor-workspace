class Solution:
    @staticmethod
    def differenceOfSums(n: int, m: int) -> int:
        # Calculate the sum of the first n natural numbers using the formula n * (n + 1) / 2
        sum_natural_numbers = n * (n + 1) // 2

        # Calculate the sum of the first n//m multiples of m
        # This is equivalent to the sum of an arithmetic series with a common difference of m
        # The number of terms in this series is n//m
        # The sum of an arithmetic series is given by n * (n + 1) / 2, where n is the number of terms
        # In this case, n = n//m
        sum_multiples_of_m = ((n // m) * (n // m + 1) * m)

        # Return the difference between the sum of the first n natural numbers and the sum of the first n//m
        # multiples of m
        return sum_natural_numbers - sum_multiples_of_m


if __name__ == '__main__':
    print(Solution.differenceOfSums(n=10, m=3))
