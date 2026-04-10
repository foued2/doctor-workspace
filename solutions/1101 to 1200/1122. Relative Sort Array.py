from typing import List


class Solution:
    @staticmethod
    def relativeSortArray(arr1: List[int], arr2: List[int]) -> List[int]:
        """
        Relative Sorting function
        """
        # Create a dictionary to store the indices of elements in arr2
        # Key: element value, Value: index in arr2
        element_indices = {element: index for index, element in enumerate(arr2)}

        # Define a custom sorting key function using a lambda function
        # The sorting key function prioritizes elements in arr2 first,
        # and then sorts the remaining elements based on their values
        def sorting_key(element):
            # If the element is in arr2, return its index in arr2
            # Otherwise, return a large value to sort it after elements in arr2
            return element_indices.get(element, 1000 + element)

        # Sort arr1 using the custom sorting key function
        sorted_arr1 = sorted(arr1, key=sorting_key)

        # Return the sorted arr1
        return sorted_arr1


print(Solution.relativeSortArray(arr1=[2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19], arr2=[2, 1, 4, 3, 9, 6]))
