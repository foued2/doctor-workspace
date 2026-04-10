from typing import List


class Solution:
    @staticmethod
    def oddCells(m: int, n: int, indices: List[List[int]]) -> int:
        # Initialize the count of cells with odd values
        ans = 0

        # Create an m x n matrix initialized with zeros
        matrix = [[0 for _ in range(n)] for _ in range(m)]

        # Iterate over each index pair (r, c) in indices
        for idx in indices:
            r, c = idx

            # Increment all elements in row r by 1
            for i in range(n):
                matrix[r][i] += 1

            # Increment all elements in column c by 1
            for i in range(m):
                matrix[i][c] += 1

        # Iterate over the matrix to count cells with odd values
        for i in range(m):
            for j in range(n):
                if matrix[i][j] % 2 != 0:
                    ans += 1

        # Return the count of cells with odd values
        return ans


print(Solution.oddCells(m=2, n=3, indices=[[0, 1], [1, 1]]))


class Solution:
    @staticmethod
    def oddCells(m: int, n: int, indices: List[List[int]]) -> int:
        """
        Bitmask, Xor, Flip bits
        """
        # Initialize a list 'mask_r' to track row increments; initially all zeros
        mask_r = [0] * m
        # Initialize a list 'mask_c' to track column increments; initially all zeros
        mask_c = [0] * n

        # Iterate over each pair of indices (r, c)
        for r, c in indices:
            # Toggle the value in mask_r at index r (1 -> 0 or 0 -> 1)
            mask_r[r] ^= 1
            # Toggle the value in mask_c at index c (1 -> 0 or 0 -> 1)
            mask_c[c] ^= 1

        # Sum the values in mask_r to count rows with an odd number of increments
        odd_rows = sum(mask_r)
        # Sum the values in mask_c to count columns with an odd number of increments
        odd_cols = sum(mask_c)

        # Calculate the total number of cells with odd values:
        # odd_rows * n gives all odd increment cells in odd_rows
        # odd_cols * m gives all odd increment cells in odd_cols
        # 2 * odd_rows * odd_cols gives the intersection cells counted twice
        total_odd_cells = (odd_rows * n) + (odd_cols * m) - (2 * odd_rows * odd_cols)

        # Return the total count of cells with odd values
        return total_odd_cells


print(Solution.oddCells(m=2, n=3, indices=[[0, 1], [1, 1]]))
