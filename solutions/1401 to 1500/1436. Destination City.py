from typing import List


class Solution:
    @staticmethod
    def destCity(paths: List[List[str]]) -> str:
        # Extract the start cities from the paths
        start_cities = [path[0] for path in paths]

        # Iterate through each path
        for path in paths:
            # Check if the destination city of the current path is not in the list of start cities
            if path[1] not in start_cities:
                # If so, return it as the destination city
                return path[1]


print(Solution.destCity(paths=[["B", "C"], ["D", "B"], ["C", "A"]]))
