from typing import List


class Solution:
    @staticmethod
    def findThePrefixCommonArray(A: List[int], B: List[int]) -> List[int]:
        # Get the length of the input lists
        n = len(A)
        # Initialize an empty list to store the results
        res = []

        # Loop through each index from 0 to n-1
        for i in range(n):
            # Create a set of the prefix of list A up to index i (inclusive)
            set_A = set(A[:i + 1])
            # Create a set of the prefix of list B up to index i (inclusive)
            set_B = set(B[:i + 1])
            # Find the intersection of the two sets (common elements)
            common_elements = set_A.intersection(set_B)
            # Append the number of common elements to the result list
            res.append(len(common_elements))

        # Return the result list containing the number of common elements for each prefix
        return res


print(Solution.findThePrefixCommonArray(A=[1, 3, 2, 4], B=[3, 1, 2, 4]))
