from typing import List


class Solution:
    @staticmethod
    def construct2DArray(original: List[int], m: int, n: int) -> List[List[int]]:
        # Check if the length of the original list matches the expected size of the 2D array
        if len(original) != m * n:
            return list()  # If not, return an empty list

        # Initialize an empty list to store the constructed 2D array
        res = list()

        # Iterate over each row
        for i in range(m):
            # Slice the original list to extract elements for the current row
            row = original[i * n:(i + 1) * n]
            # Append the sliced row to the result list
            res.append(row)

        # Return the constructed 2D array
        return res


# Test the function
if __name__ == '__main__':
    print(Solution.construct2DArray(original=[1, 2, 3], m=1, n=3))
