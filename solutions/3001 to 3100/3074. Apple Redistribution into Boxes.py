from typing import List


class Solution:
    @staticmethod
    def minimumBoxes(apple: List[int], capacity: List[int]) -> int:
        """
        Greedy
        """
        # Sort the capacities in reverse order to consider larger boxes first
        capacity = sorted(capacity, reverse=True)
        # Calculate the total number of apples
        total_apples = sum(apple)
        # Initialize a counter to keep track of the number of boxes used
        boxes_used = 0

        # Iterate through the capacities of boxes
        for i in range(len(capacity)):
            # Check if there are still apples to pack
            if total_apples > 0:
                # Increment the counter to represent using one more box
                boxes_used += 1
                # Calculate the number of apples that can be packed into the current box
                apples_packed = min(total_apples, capacity[i])
                # Subtract the number of packed apples from the total
                total_apples -= apples_packed
            else:
                # If there are no more apples to pack, exit the loop
                break

        # Return the minimum number of boxes needed to pack all apples
        return boxes_used


if __name__ == '__main__':
    print(Solution.minimumBoxes(apple=[1, 3, 2], capacity=[4, 3, 1, 5, 2]))
    print(Solution.minimumBoxes(apple=[5, 5, 5], capacity=[2, 4, 2, 7]))