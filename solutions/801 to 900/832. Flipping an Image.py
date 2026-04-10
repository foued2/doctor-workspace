from typing import List


class Solution:
    @staticmethod
    def flipAndInvertImage(image: List[List[int]]) -> List[List[int]]:
        # Iterate through each row in the image
        for row in image:
            # Reverse the current row in place
            row.reverse()
            # Iterate through each bit in the row and invert it in place
            for i in range(len(row)):
                row[i] ^= 1  # Invert the bit in place

        # Return the modified image
        return image


print(Solution.flipAndInvertImage(image=[[1, 1, 0, 0], [1, 0, 0, 1], [0, 1, 1, 1], [1, 0, 1, 0]]))
