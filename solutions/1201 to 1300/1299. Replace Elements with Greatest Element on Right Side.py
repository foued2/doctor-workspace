from typing import List


class Solution:
    @staticmethod
    def replaceElements(arr: List[int]) -> List[int]:
        n = len(arr)
        res = [-1] * n  # Initialize the result array with -1
        max_from_right = -1  # Initialize the maximum element seen from the right

        # Iterate from the rightmost element to the left
        for i in range(n - 1, -1, -1):
            res[i] = max_from_right  # Update the current position with max_from_right
            max_from_right = max(max_from_right, arr[i])  # Update max_from_right

        return res


print(Solution.replaceElements(arr=[17, 18, 5, 4, 6, 1]))
