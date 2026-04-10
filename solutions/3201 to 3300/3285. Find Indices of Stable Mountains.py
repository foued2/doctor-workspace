from typing import List


class Solution:
    @staticmethod
    def stableMountains(height: List[int], threshold: int) -> List[int]:
        # This list will store the result indices
        res = []
        # Get the total number of elements in the height list
        n = len(height)

        # Iterate through each element in the height list (starting from the second element)
        for i in range(1, n):
            # If the previous element height is greater than the threshold,
            # add the current index to the result list
            if height[i - 1] > threshold:
                res.append(i)

        # Return the result list containing indices
        return res


# Example usage to print the indices of stable mountains
if __name__ == '__main__':
    print(Solution().stableMountains([1, 2, 3, 4, 3, 2, 1], 1))