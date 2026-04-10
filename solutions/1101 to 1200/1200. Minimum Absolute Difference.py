from typing import List


class Solution:
    @staticmethod
    def minimumAbsDifference(arr: List[int]) -> List[List[int]]:
        # Sort the array
        arr.sort()

        # Initialize variables to track the minimum absolute difference and the result list
        min_diff = float('inf')
        res = []

        # Iterate through the array to find the minimum absolute difference
        for i in range(len(arr) - 1):
            # Calculate the absolute difference between adjacent elements
            diff = arr[i + 1] - arr[i]

            # Update the minimum absolute difference
            if diff < min_diff:
                min_diff = diff
                res = [[arr[i], arr[i + 1]]]
            elif diff == min_diff:
                # If the absolute difference equals the minimum, add the pair to the result list
                res.append([arr[i], arr[i + 1]])

        # Return the result list
        return res


# Test the function
print(Solution.minimumAbsDifference(arr=[4, 2, 1, 3]))
