from typing import List


class Solution:
    @staticmethod
    def duplicateZeros(arr: List[int]) -> None:
        # Find the starting length of the array
        starting_length = len(arr)

        # Initialize a pointer for the current index
        i = 0

        # Iterate over the array
        while i < starting_length:
            # If a zero is found
            if arr[i] == 0:
                # Insert a zero at the next position
                arr.insert(i + 1, 0)

                # Remove the last element to keep the array length constant
                arr.pop()

                # Move the index to the next position to skip the inserted zero
                i += 1

            # Move to the next element
            i += 1


# Example usage:
arr = [1, 0, 2, 3, 0, 4, 5, 0]
Solution().duplicateZeros(arr)
print(arr)  # Output should be [1, 0, 0, 2, 3, 0, 0, 4]
