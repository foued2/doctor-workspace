from typing import List
from collections import defaultdict


class Solution:
    @staticmethod
    def maximumPopulation(logs: List[List[int]]) -> int:
        # Initialize a defaultdict to hold population changes
        pop_changes = defaultdict(int)

        # Track the maximum year range from the logs
        start_year = float('inf')
        end_year = float('-inf')

        # Apply population changes at birth and death years
        for birth, death in logs:
            pop_changes[birth] += 1
            pop_changes[death] -= 1
            start_year = min(start_year, birth)
            end_year = max(end_year, death)

        # Initialize variables for prefix sum approach
        max_population = 0
        current_population = 0
        max_population_year = start_year

        # Iterate through the years and calculate the prefix sum of population
        for year in range(start_year, end_year + 1):
            current_population += pop_changes[year]
            if current_population > max_population:
                max_population = current_population
                max_population_year = year

        return max_population_year


if __name__ == '__main__':
    logs_data = [[2033, 2034], [2039, 2047], [1998, 2042],
                 [2047, 2048], [2025, 2029], [2005, 2044],
                 [1990, 1992], [1952, 1956], [1984, 2014]]
    print(Solution.maximumPopulation(logs_data))