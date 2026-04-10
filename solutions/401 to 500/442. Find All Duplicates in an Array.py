from typing import List


class Solution:
    @staticmethod
    def findDuplicates(nums: List[int]) -> List[int]:
        # Initialize an empty dictionary to store the frequency of each element
        res = dict()
        # Initialize an empty list to store the duplicate elements
        sol = list()

        # Iterate through each element in the input list
        for num in nums:
            # If the element is already in the dictionary, it's a duplicate
            if num in res:
                # Increment the frequency count of the element
                res[num] += 1
                # If the frequency count exceeds 1, add the element to the solution list
                if res[num] > 1:
                    sol.append(num)
            else:
                # If the element is not in the dictionary, add it with a frequency count of 1
                res[num] = 1

        # Return the list of duplicate elements found
        return sol


# Test the function
print(Solution.findDuplicates([4, 3, 2, 7, 8, 2, 3, 1]))
