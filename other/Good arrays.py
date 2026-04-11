class Solution:
    @staticmethod
    def digit_sum(num: int) -> int:
        # Calculate the sum of digits of a number
        total = 0
        while num:
            total += num % 10
            num //= 10
        return total

    @staticmethod
    def c(n: int) -> int:
        dp = [0] * (n + 1)
        for i in range(1, n + 1):
            digit_sum = Solution.digit_sum(i)
            dp[i] = dp[i - 1] + digit_sum
        return dp[-1]


# Test the optimized method
print(Solution.c(7))   # Test case given in your example
print(Solution.c(1434)) # The 5th number in your example
print(Solution.c(2024)) # The 6th number in your example
print(Solution.c(200000)) # The 7th number in your example


t = int(input())
for _ in range(t):
    n = int(input())
    print(Solution.c(n))
