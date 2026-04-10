class Solution:
    @staticmethod
    def dayOfYear(date: str) -> int:
        ans = 0  # Initialize the day of the year counter
        year, month, day = map(int, date.split('-'))  # Extract year, month, and day from the input date
        months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # Number of days in each month

        # Function to determine if a given year is a leap year
        def leapYear(year: int) -> bool:
            return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

        # Adjust the number of days in February for leap years
        if leapYear(year):
            months[1] = 29

        # Calculate the day of the year
        for i in range(month - 1):  # Iterate through months before the given month
            ans += months[i]  # Add the number of days in each month to the counter
        return ans + day  # Add the day of the given month to the counter and return the result


print(Solution.dayOfYear(date="2019-01-09"))
