from typing import List


class Solution:
    @staticmethod
    def findContentChildren(g: List[int], s: List[int]) -> int:
        # Sort the lists of children's greed factors and cookie sizes
        g.sort()
        s.sort()

        # Initialize pointers and count of content children
        i, j, content_children = 0, 0, 0

        # Iterate through the lists
        while i < len(g) and j < len(s):
            # If the current cookie size can satisfy the current child's greed factor,
            # move to the next child and cookie, and increment the count of content children
            if s[j] >= g[i]:
                content_children += 1
                i += 1
            j += 1  # Move to the next cookie regardless

        return content_children

