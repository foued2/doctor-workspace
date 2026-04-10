from collections import defaultdict
from typing import List


class Solution:
    @staticmethod
    def occurrencesOfElement(nums: List[int], queries: List[int], x: int) -> List[int]:
        # Get the length of the input list nums
        n = len(nums)

        # Initialize the result list to store answers for each query
        res = []

        # Initialize a default dictionary to store lists of indices for each element
        table = defaultdict(list)

        # Iterate over the list nums to record the indices where x occurs
        for i in range(n):
            # Check if the current element is equal to x
            if nums[i] == x:
                # If it is, append the index i to the list for x in the dictionary
                table[x].append(i)

        # Get the list of occurrences of x
        occurrences = list(table[x])

        # Process each query
        for query in queries:
            # If the query is greater than the number of occurrences, append -1 to result
            if query > len(occurrences):
                res.append(-1)
            else:
                # Otherwise, append the (query-1)th occurrence's index to result
                res.append(occurrences[query - 1])

        # Return the result list containing answers to all queries
        return res


print(Solution.occurrencesOfElement(nums=[1, 3, 1, 7], queries=[1, 3, 2, 4], x=1))
