from typing import List


class Solution:
    @staticmethod
    def kidsWithCandies(candies: List[int], extraCandies: int) -> List[bool]:
        # Calculate the number of elements in the candy list
        n = len(candies)
        # Initialize an empty list to store the result
        res = []
        # Iterate through each element in the candy list
        for i in range(n):
            # Check if adding extraCandies to the current child's candies is greater than or equal to the maximum
            # candies among all children
            if candies[i] + extraCandies >= max(candies):
                # If the condition is true, append True to the result list
                res.append(True)
            else:
                # If the condition is false, append False to the result list
                res.append(False)

        return res


if __name__ == '__main__':
    # Test the function with a sample input
    print(Solution.kidsWithCandies(candies=[2, 3, 5, 1, 3], extraCandies=3))
