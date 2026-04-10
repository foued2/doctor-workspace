from typing import List
from collections import Counter


class Solution:
    @staticmethod
    def mergeSimilarItems(items1: List[List[int]], items2: List[List[int]]) -> List[List[int]]:
        # Convert the lists of items to dictionaries and then to Counters to combine their counts
        dict1 = {item[0]: item[1] for item in items1}
        dict2 = {item[0]: item[1] for item in items2}
        counter1 = Counter(dict1)
        counter2 = Counter(dict2)

        # Combine the two Counters by adding them
        combined_counter = counter1 + counter2

        # Convert the combined Counter back to a list of lists and sort by the item values (keys)
        sorted_items = sorted(combined_counter.items())

        # Convert tuples to lists for the final output
        return [[key, value] for key, value in sorted_items]


# Example usage:
solution = Solution()
result = solution.mergeSimilarItems([[1, 3], [2, 2]], [[1, 1], [3, 2]])
print(result)  # Output: [[1, 4], [2, 2], [3, 2]]
