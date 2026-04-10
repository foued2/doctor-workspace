from typing import List


class Solution:
    @staticmethod
    def canBeEqual(target: List[int], arr: List[int]) -> bool:
        """
        Hash table
        """
        # Create a dictionary to store the frequency of elements in the target list
        frequency_map = {}

        # Count the frequency of elements in a target list
        for element in target:
            frequency_map[element] = frequency_map.get(element, 0) + 1

        # Iterate through arr and decrement the count of each element in the dictionary
        for element in arr:
            if element not in frequency_map or frequency_map[element] == 0:
                # If the element is not present in a target list or its count becomes zero, the lists are not equal
                return False
            frequency_map[element] -= 1

        # Check if all frequencies in frequency_map are zero
        return all(count == 0 for count in frequency_map.values())


if __name__ == '__main__':
    print(Solution.canBeEqual(target=[1, 2, 3, 4], arr=[2, 4, 1, 3]))


class Solution:
    @staticmethod
    def canBeEqual(arr1: List[int], arr2: List[int]) -> bool:
        # Sort the first array
        arr1.sort()
        # Sort the second array
        arr2.sort()
        # Compare the sorted arrays and return True if they are identical, else False
        return arr1 == arr2


# Example usage
if __name__ == '__main__':
    # Test arrays
    arr1 = [1, 2, 3, 4]
    arr2 = [2, 4, 1, 3]

    # Call the canBeEqual function and print the result
    print(Solution.canBeEqual(arr1, arr2))