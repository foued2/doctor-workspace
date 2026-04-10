from typing import List


class Solution:
    @staticmethod
    def numSpecial(mat: List[List[int]]) -> int:
        # Create a dictionary to count the number of '1's in each column
        # Using zip(*mat) to transpose the matrix and enumerate to get column index
        col_count = {j: list(arr).count(1) for j, arr in enumerate(zip(*mat))}

        # Initialize the result to store the count of special positions
        result = 0

        # Loop through each row in the matrix
        for row in mat:
            # If there is no '1' in the current row, skip to the next row
            if 1 not in row:
                continue

            # Check if the current row contains exactly one '1'
            if row.count(1) == 1:
                # Find the column index of the '1' in the current row
                col_index = row.index(1)

                # Check if the column also contains exactly one '1'
                if col_count[col_index] == 1:
                    # Increment the result as we found a special position
                    result += 1

        # Return the final count of special positions
        return result


print(Solution.numSpecial(
    mat=[[0, 0, 0, 0, 0, 1, 0, 0],
         [0, 0, 0, 0, 1, 0, 0, 1],
         [0, 0, 0, 0, 1, 0, 0, 0],
         [1, 0, 0, 0, 1, 0, 0, 0],
         [0, 0, 1, 1, 0, 0, 0, 0]]))
