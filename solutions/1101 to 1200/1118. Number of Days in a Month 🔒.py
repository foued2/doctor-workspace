class Solution:
    @staticmethod
    def numberOfDays(year: int, month: int) -> int:
        # Helper function to determine if a given year is a leap year
        def leapYear(year: int) -> bool:
            # A leap year is divisible by 4 but not by 100, or it is divisible by 400
            return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

        # Array containing the number of days in each month for a non-leap year
        months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # If the year is a leap year, update the number of days in February
        if leapYear(year):
            months[1] = 29

        # Return the number of days in the specified month (month is 1-based, so subtract 1 for 0-based index)
        return months[month - 1]


# Example usage
solution = Solution()
print(solution.numberOfDays(2020, 2))  # Output: 29 (2020 is a leap year)
print(solution.numberOfDays(2019, 2))  # Output: 28 (2019 is not a leap year)
print(solution.numberOfDays(2024, 4))  # Output: 30 (April has 30 days)

