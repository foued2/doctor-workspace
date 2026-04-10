from typing import List


class Solution:
    @staticmethod
    def arraysIntersection(arr1: List[int], arr2: List[int], arr3: List[int]) -> List[int]:
        """
        Binary search
        """
        # Define a helper function for binary search
        def binarySearch(arr: List[int], target: int) -> bool:
            left, right = 0, len(arr) - 1
            while left <= right:
                mid = (left + right) // 2
                if arr[mid] == target:
                    return True
                elif arr[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1
            return False

        # Initialize an empty list to store the intersection
        res = []
        nums = []

        # Iterate through the elements of the first array
        for num in arr1:
            # Check if the current element exists in the second array
            if binarySearch(arr2, num):
                nums.append(num)

        # Iterate through the elements found in the second array
        for num in nums:
            # Check if the current element exists in the third array
            if binarySearch(arr3, num):
                # If it does, add it to the intersection list
                res.append(num)

        # Return the intersection list
        return res


print(Solution.arraysIntersection(arr1=[1, 2, 3, 4, 5], arr2=[1, 2, 5, 7, 9], arr3=[1, 3, 4, 5, 8]))


class Solution:
    @staticmethod
    def arraysIntersection(arrays: List[List[int]]) -> List[int]:
        """
        Two pointers
        """
        # Initialize intersection as the first list
        intersection = arrays[0]

        # Iterate through the remaining lists
        for arr in arrays[1:]:
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


print(Solution.arraysIntersection(arrays=[[1, 2, 3], [1, 2, 5, 7, 9], [1, 3, 4, 5]]))
