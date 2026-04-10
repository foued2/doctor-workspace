class Solution:
    @staticmethod
    def consecutiveNumbersSum(n: int) -> int:
        """
        Count the number of ways to write a positive integer n as the sum of consecutive positive integers.

        Approach: 1. Represent n as the product of its odd factors.
        2. Each odd factor corresponds to a possible
        solution.
        3. For each odd factor, calculate the count of its occurrences in the factorization of n. 4.
        Multiply the counts of all odd factors to get the total number of solutions.
        5. If n == 1, all prime factors
        have been found.
        Otherwise, multiply the total by 2 to account for the case when n itself is a single number.
        """

        # Initialize the total number of solutions
        total_solutions = 1
        # Start with the smallest odd prime factor, 3
        current_factor = 3

        # Step 1: Factorize n by discarding all factors divisible by 2
        while n % 2 == 0:
            n //= 2

        # Step 2: Check odd factors
        while current_factor * current_factor <= n:
            # Initialize the count of occurrences of the current factor
            factor_count = 0
            # Step 3: Calculate the count of occurrences of the current factor
            while n % current_factor == 0:
                n //= current_factor
                factor_count += 1
            # Step 4: Multiply the total by the count of occurrences of the current factor plus 1
            total_solutions *= factor_count + 1
            # Move to the next odd factor
            current_factor += 2

        # Step 5: If n == 1, all prime factors have been found.
        # Otherwise, multiply the total by 2 to account for the
        # case when n itself is a single number.
        return total_solutions if n == 1 else total_solutions * 2


print(Solution.consecutiveNumbersSum(n=15))  # Example usage
