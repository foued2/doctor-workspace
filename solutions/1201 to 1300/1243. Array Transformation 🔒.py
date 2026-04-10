from typing import List


class Solution:
    @staticmethod
    def transformArray(arr: List[int]) -> List[int]:
        """
        Flag
        """
        n = len(arr)

        # Repeat the transformation process until no changes occur
        while True:
            # Initialize a flag to track if any changes happen during the iteration
            changed = False

            # Create a copy of the current array to store the next day's state
            next_day = arr.copy()

            # Traverse the array elements from the second to the second-last element
            for i in range(1, n - 1):
                # If an element is greater than both its neighbors, decrease it by 1
                if arr[i] > arr[i - 1] and arr[i] > arr[i + 1]:
                    next_day[i] = arr[i] - 1
                    # Set changed flag to True to indicate a change has occurred
                    changed = True
                # If an element is smaller than both its neighbors, increase it by 1
                elif arr[i] < arr[i - 1] and arr[i] < arr[i + 1]:
                    next_day[i] = arr[i] + 1
                    # Set changed flag to True to indicate a change has occurred
                    changed = True

            # If no changes were made during the iteration, break out of the loop
            if not changed:
                break

            # Update the array to the new transformed values for the next iteration
            arr = next_day

        # Return the final transformed array
        return arr


# Example usage
if __name__ == '__main__':
    print(Solution.transformArray(arr=[1, 6, 3, 4, 3, 5]))
    