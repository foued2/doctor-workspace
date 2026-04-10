from typing import List


class Solution:
    @staticmethod
    def average(salary: List[int]) -> float:
        # Get the number of elements in the list
        n = len(salary)

        # Initialize variables to store minimum and maximum salaries
        min_salary = (10 ** 6) + 1  # Initialize min_salary to a large value
        max_salary = 999  # Initialize max_salary to a small value

        # Initialize variable to store the total sum of salaries
        total_sum = 0

        # Iterate through the list of salaries
        for i in range(n):
            # Update min_salary if the current salary is smaller
            min_salary = min(min_salary, salary[i])

            # Update max_salary if the current salary is larger
            max_salary = max(max_salary, salary[i])

            # Add the current salary to the total sum
            total_sum += salary[i]

        # Subtract the minimum and maximum salaries from the total sum
        total_sum -= (min_salary + max_salary)

        # Calculate the average by dividing the total sum by the number of salaries minus 2
        return total_sum / (n - 2)


print(Solution.average(salary=[4000, 3000, 1000, 2000]))
