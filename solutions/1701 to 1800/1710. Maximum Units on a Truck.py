from typing import List


class Solution:
    @staticmethod
    def maximumUnits(boxTypes: List[List[int]], truckSize: int) -> int:
        # Initialize the total size (number of boxes loaded onto the truck) to 0
        size = 0
        # Sort the boxTypes list in descending order based on the number of units per box
        boxTypes.sort(key=lambda x: x[1], reverse=True)
        # Initialize the total load (number of units loaded onto the truck) to 0
        load = 0
        # Iterate over each type of box in the sorted list
        for box in boxTypes:
            # If the truck can carry more boxes, add as many boxes of the current type as possible
            if size < truckSize:
                # Calculate the number of boxes we can take of this type without exceeding the truck's capacity
                boxes_to_take = min(box[0], truckSize - size)
                # Add the corresponding units to the total load
                load += boxes_to_take * box[1]
                # Update the size with the number of boxes added
                size += boxes_to_take
            else:
                # If the truck is full, return the total load
                return load
        # Return the total load if all box types have been processed
        return load


# Example usage:
# boxTypes = [[1, 3], [2, 2], [3, 1]]
# truckSize = 4
# print(Solution.maximumUnits(boxTypes, truckSize))  # Output should be 8


# Example usage:
boxTypes = [[1, 3], [2, 2], [3, 1]]
truckSize = 4
print(Solution.maximumUnits(boxTypes, truckSize))  # Expected output: 8

print(Solution.maximumUnits(boxTypes=[[5, 10], [2, 5], [4, 7], [3, 9]], truckSize=10))
