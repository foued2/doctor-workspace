from typing import List


class Solution:
    @staticmethod
    def hIndex(citations: List[int]) -> int:
        # Get the number of elements in the citations list
        n = len(citations)

        # Initialize a counter to keep track of the number of citations
        counter = 0

        # Sort the citations list in non-decreasing order
        citations.sort(reverse=True)

        # Iterate through the citations list
        for i in range(n):
            # Check if the current citation count is greater than or equal to the number of papers with at least that
            # many citations
            if citations[i] >= i + 1:
                # Increment the counter as the current citation count satisfies the H-index condition
                counter += 1

        # Return the calculated H-index
        return counter


# Test the solution with the given example
print(Solution.hIndex(citations=[11,15]))
