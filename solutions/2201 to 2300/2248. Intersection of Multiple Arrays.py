from typing import List


class Solution:
    @staticmethod
    def intersection(nums: List[List[int]]) -> List[int]:
        """
        Two pointers
        """
        # Initialize intersection as the first list
        intersection = nums[0]

        # Iterate through the remaining lists
        for arr in nums[1:]:
            # Initialize a new list to store the intersection between the current list and the previous intersection
            new_intersection = []
            # Initialize pointers for both lists
            i, j = 0, 0
            # Iterate until one of the lists reaches its end
            while i < len(intersection) and j < len(arr):
                # If the elements are equal, add to the new intersection
                if intersection[i] == arr[j]:
                    new_intersection.append(intersection[i])
                    i += 1
                    j += 1
                # Move the pointer of the smaller element's list forward
                elif intersection[i] < arr[j]:
                    i += 1
                else:
                    j += 1
            # Update the intersection with the new intersection
            intersection = new_intersection

        return intersection


print(Solution.intersection(nums=[[3, 1, 2, 4, 5], [1, 2, 3, 4], [3, 4, 5, 6]]))
