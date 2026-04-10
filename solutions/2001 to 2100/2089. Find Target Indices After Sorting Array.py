from typing import List, Any


class Solution:
    @staticmethod
    def targetIndices(nums: List[int], target: int) -> List[int]:
        # Sort the input list
        nums.sort()

        # Initialize variables for binary search
        low, high = 0, len(nums) - 1
        left_index, right_index = -1, -1

        # Binary search for the leftmost index of the target element
        while low <= high:
            mid = (low + high) >> 1  # Calculate middle index
            if nums[mid] == target:
                left_index = mid  # Update leftmost index
                high = mid - 1  # Search in the left half
            elif nums[mid] > target:
                high = mid - 1  # Search in the left half
            else:
                low = mid + 1  # Search in the right half

        # Reset search range for finding the rightmost index
        low, high = left_index, len(nums) - 1

        # Binary search for the rightmost index of the target element
        while low <= high:
            mid = (low + high) >> 1  # Calculate middle index
            if nums[mid] == target:
                right_index = mid  # Update rightmost index
                low = mid + 1  # Search in the right half
            elif nums[mid] > target:
                high = mid - 1  # Search in the left half
            else:
                low = mid + 1  # Search in the right half

        # If the target is not found, return an empty list
        if left_index == -1:
            return []

        # Generate the list of indices containing the target element
        target_indices = list(range(left_index, right_index + 1))
        return target_indices


if __name__ == '__main__':
    print(Solution.targetIndices(nums=[1, 2, 5, 2, 3], target=2))


from typing import List, Any


class Solution:
    @staticmethod
    def targetIndices(nums: List[int], target: int) -> List[int]:
        # Find Occurrence of Target
        def binary_search_first_occurrence(arr: List[int], target: int) -> list[int | Any]:
            """
            Finds the occurrence of the target in the sorted array.
            Returns the list of the occurrences of target.
            """
            left, right = 0, len(arr) - 1
            result = []
            while left <= right:  # Binary search loop
                mid = left + (right - left) // 2  # Find middle index
                if arr[mid] == target:
                    result.append(mid)  # Add occurrence index to result
                    right = mid - 1  # Keep searching in the left half
                elif arr[mid] < target:
                    left = mid + 1  # Move left boundary rightward
                else:
                    right = mid - 1  # Move right boundary leftward
            return result

        nums.sort()  # Sort the input list
        return binary_search_first_occurrence(nums, target)  # Use helper function to get target indices


if __name__ == '__main__':
    print(Solution.targetIndices(nums=[1, 2, 5, 2, 3], target=2))