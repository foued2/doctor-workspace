from typing import List


class Solution:
    @staticmethod
    def checkIfExist(arr: List[int]) -> bool:
        # Get the length of the input array
        n = len(arr)

        # Initialize a dictionary to keep track of the elements we have seen
        table = {}

        # Iterate over each element in the array
        for i in range(n):
            # Check if the current element is even and if half of its value exists in the table
            if arr[i] % 2 == 0 and arr[i] // 2 in table:
                return True  # If found, return True

            # Check if double the current element exists in the table
            elif 2 * arr[i] in table:
                return True  # If found, return True

            # Add the current element to the table
            else:
                table[arr[i]] = True

        # If no such pair is found, return False
        return False


print(Solution.checkIfExist(arr=[3, 1, 7, 11]))


class Solution:
    @staticmethod
    def checkIfExist(arr: List[int]) -> bool:
        """
        Binary search, Target
        """
        # Sort the array to use binary search
        arr.sort()

        # Iterate through each element in the array
        for current_index in range(len(arr)):
            target_double = arr[current_index] * 2  # Calculate the target value which is double the current element
            low, high = 0, len(arr) - 1  # Initialize binary search pointers

            # Perform binary search to find the target_double
            while low <= high:
                mid = (low + high) // 2  # Calculate the middle index

                # Check if the middle element is the target_double and not the current element itself
                if arr[mid] == target_double and mid != current_index:
                    return True  # Found the element which is double the current element

                # If the middle element is less than the target, search in the right half
                elif arr[mid] < target_double:
                    low = mid + 1

                # If the middle element is greater than the target, search in the left half
                else:
                    high = mid - 1

        # If no such pair is found, return False
        return False


# Example usage
solution = Solution()
print(solution.checkIfExist([-10, 12, -20, -8, 15]))  # Output: True
print(solution.checkIfExist([10, 2, 5, 3]))  # Output: True
print(solution.checkIfExist([7, 1, 14, 11]))  # Output: True
print(solution.checkIfExist([3, 1, 7, 11]))  # Output: False
