import math


class Solution:
    @staticmethod
    def countTriples(n: int) -> int:
        # Initialize the count of valid triples to 0
        ans = 0

        # Iterate over all possible values of a from 1 to n-1
        for a in range(1, n):
            # Iterate over all possible values of b from 1 to n-1
            for b in range(1, n):
                # Calculate c as the square root of (a^2 + b^2)
                c = math.sqrt((a ** 2) + (b ** 2))

                # Check if c is an integer and lies within the range 1 to n-1
                if c.is_integer() and int(c) <= n:
                    # If valid, increment the count of triples
                    ans += 1

        # Return the total count of valid triples
        return ans


# Example usage
solution = Solution()
print(solution.countTriples(10))  # Output will be the count of Pythagorean triples where a, b, c ≤ 10

print(Solution.countTriples(n=5))
