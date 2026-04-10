from typing import List


class Solution:
    @staticmethod
    def sortPeople(names: List[str], heights: List[int]) -> List[str]:
        # Initialize an empty list to store the sorted names
        res = []

        # Combine the names and heights into tuples using zip()
        zipped = zip(heights, names)

        # Sort the tuples based on heights in descending order
        for item in sorted(zipped, reverse=True):
            # Append the name (the second element of each tuple) to the result list
            res.append(item[1])

        # Return the sorted list of names
        return res


print(Solution.sortPeople(names=["Alice", "Bob", "Bob"], heights=[155, 185, 150]))
