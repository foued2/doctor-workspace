import sys

# Increase recursion depth just in case, though the max depth
# for 12 digits is small.
sys.setrecursionlimit(2000)


def solve_euler_719():
    N = 10 ** 12
    limit = int(N ** 0.5)
    total_sum = 0

    # Recursive function to check if n can be split into parts summing to target
    def check(n, target):
        # If the remaining number matches the target, it's a valid path
        if n == target:
            return True

        # If n < target, we cannot split n further to sum to target
        # because the sum of parts of a number is <= the number itself.
        if n < target:
            return False

        # Try splitting n at different positions
        m = 10
        while m <= n:
            r = n % m
            l = n // m

            # Optimization: The right part r contributes directly to the sum.
            # If r exceeds the target, this split and any larger m are invalid.
            if r > target:
                break

            # Recurse on the left part with the reduced target
            if check(l, target - r):
                return True

            m *= 10

        return False

    for i in range(2, limit + 1):
        # Optimization: A number n can only be split into parts summing to sqrt(n)
        # if sqrt(n) == n (mod 9). This implies i == i*i (mod 9),
        # which only holds for i % 9 == 0 or i % 9 == 1.
        if (i % 9) != 0 and (i % 9) != 1:
            continue

        n = i * i

        # The recursive check allows taking the whole number n as one part.
        # However, the problem requires "two or more numbers".
        # Since n = i*i and i >= 2, n > i always.
        # Therefore, check(n, i) will never match n == target immediately.
        # It forces at least one split in the loop, satisfying the condition.
        if check(n, i):
            total_sum += n

    return total_sum


if __name__ == "__main__":
    result = solve_euler_719()
    print(f"Solution: {result}")