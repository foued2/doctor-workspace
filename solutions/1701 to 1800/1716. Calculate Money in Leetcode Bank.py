class Solution:
    @staticmethod
    def totalMoney(n: int) -> int:
        # Calculate the number of complete weeks and the remaining days
        quotient, remainder = divmod(n, 7)

        # Calculate the money saved in complete weeks
        # Each week, the savings pattern is 1, 2, 3, 4, 5, 6, 7
        # The sum of savings for one week is the sum of first 7 natural numbers
        # Sum of first 7 natural numbers is (7 * (7 + 1)) // 2 = 28
        # For quotient complete weeks, we add an increasing amount each week:
        # Week 1: 1+2+3+4+5+6+7 = 28
        # Week 2: 2+3+4+5+6+7+8 = 28 + 7
        # Week 3: 3+4+5+6+7+8+9 = 28 + 2*7
        # Total for quotient weeks: (28 * quotient) + (sum of first (quotient-1) natural numbers) * 7
        # sum of first (quotient-1) natural numbers is (quotient * (quotient - 1)) // 2
        complete_weeks_sum = 28 * quotient + 7 * (quotient * (quotient - 1)) // 2

        # Calculate the money saved in the remaining days
        # For the remaining days, we start from the next week's starting value
        # For example, if quotient is 2, the starting value for the remaining days is 3
        remaining_days_sum = 0
        start_value = quotient + 1
        for i in range(remainder):
            remaining_days_sum += start_value + i

        # Total money saved is the sum of money saved in complete weeks and remaining days
        ans = complete_weeks_sum + remaining_days_sum

        return ans


# Example usage:
sol = Solution()
print(sol.totalMoney(4))  # Expected output: 10 (1+2+3+4)
print(sol.totalMoney(10))  # Expected output: 37 (1+2+3+4+5+6+7+2+3+4)
print(sol.totalMoney(20))  # Expected output: 96
