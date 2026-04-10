from typing import List


class Solution:
    @staticmethod
    def reformatDate(date: str) -> str:
        # Split the date string into its components: day, month, and year
        date_parts = date.split()

        # Extract the day part and remove the suffix ('st', 'nd', 'rd', 'th')
        day = date_parts[0][:-2]

        # If the day is a single digit, prepend a '0' to it
        if int(day) <= 9:
            day = '0' + day

        # List of month abbreviations
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Find the index of the month abbreviation and convert it to a 2-digit format
        month = months.index(date_parts[1]) + 1
        if month <= 9:
            month = '0' + str(month)
        else:
            month = str(month)

        # Extract the year part
        year = date_parts[-1]

        # Format the date in 'Year-Month-Day' format
        reformatted_date = f"{year}-{month}-{day}"

        # Return the reformatted date
        return reformatted_date


print(Solution.reformatDate(date="20th Oct 2052"))
