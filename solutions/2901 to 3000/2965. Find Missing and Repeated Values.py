from typing import List


class Solution:
    @staticmethod
    def findMissingAndRepeatedValues(grid: List[List[int]]) -> List[int]:
        # The length of one side of the grid
        n = len(grid)

        # The total number of elements in the grid, which should be n^2
        total_elements = n * n

        # The expected sum of the first n^2 natural numbers
        expected_sum = total_elements * (total_elements + 1) // 2

        # Calculate the actual sum of all elements in the grid
        actual_sum = sum(sum(row) for row in grid)

        # Calculate the actual sum of squares of all elements in the grid
        actual_sum_of_squares = sum(sum(x * x for x in row) for row in grid)

        # The expected sum of squares of the first n^2 natural numbers
        expected_sum_of_squares = sum(i * i for i in range(1, total_elements + 1))

        # The difference between the expected and actual sums gives us:
        sum_diff = expected_sum - actual_sum  # missing_number - repeated_number

        # The difference between the expected and actual sum of squares gives us:
        sum_of_squares_diff = expected_sum_of_squares - actual_sum_of_squares  # missing_number^2 - repeated_number^2

        # Using the equations:
        # missing_number - repeated_number = sum_diff
        # missing_number^2 - repeated_number^2 = sum_of_squares_diff
        # We can solve for missing_number and repeated_number

        # missing_number^2 - repeated_number^2 = (missing_number - repeated_number) * (missing_number + repeated_number)
        # sum_of_squares_diff = sum_diff * (missing_number + repeated_number)

        # missing_number + repeated_number = sum_of_squares_diff / sum_diff
        sum_plus = sum_of_squares_diff // sum_diff

        # Solve the two equations:
        # missing_number - repeated_number = sum_diff
        # missing_number + repeated_number = sum_plus

        missing_number = (sum_diff + sum_plus) // 2
        repeated_number = sum_plus - missing_number

        # Return the results as a list
        return [repeated_number, missing_number]


print(Solution.findMissingAndRepeatedValues(grid=[[9, 1, 7], [8, 9, 2], [3, 4, 6]]))
