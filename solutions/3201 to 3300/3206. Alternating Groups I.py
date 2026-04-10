from typing import List


class Solution:
    @staticmethod
    def numberOfAlternatingGroups(colors: List[int]) -> int:
        n = len(colors)
        count = 0

        # Iterate over each tile to check for alternating groups
        for i in range(n):
            # The three indices to check: current, left, and right
            left = colors[(i - 1) % n]
            middle = colors[i]
            right = colors[(i + 1) % n]

            # Check if the middle tile has a different color from both neighbors
            if left != middle and middle != right:
                count += 1

        return count


if __name__ == "__main__":
    print(Solution.numberOfAlternatingGroups(colors=[0, 1, 0, 0, 1]))
