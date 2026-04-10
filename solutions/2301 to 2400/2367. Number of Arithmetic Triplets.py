from typing import List


class Solution:
    @staticmethod
    def arithmeticTriplets(nums: List[int], difference: int) -> int:
        """
        Binary search
        """
        def binary_search(nums: List[int], target: int) -> bool:
            # Initialize start and end indices for binary search
            start, end = 0, len(nums) - 1

            # Perform binary search
            while start <= end:
                mid = (start + end) // 2  # Calculate the middle index
                if nums[mid] == target:  # If target is found, return True
                    return True
                elif nums[mid] > target:  # If the target is smaller, search in the left half
                    end = mid - 1
                else:  # If the target is larger, search in the right half
                    start = mid + 1

            # If the target is not found, return False
            return False

        # Get the length of the input list
        n = len(nums)

        # Initialize a variable to count arithmetic triplets
        count = 0

        # Iterate through the list up to the third-to-last element
        for i in range(n - 2):
            # Check if there exist two elements following nums[i] at a distance of 'difference' and '2*difference'
            x = binary_search(nums[i + 1:], nums[i] + difference)
            y = binary_search(nums[i + 1:], nums[i] + (2 * difference))

            # If both x and y are True, increment the count
            if x and y:
                count += 1

        # Return the count of arithmetic triplets
        return count


# Example usage:
print(Solution.arithmeticTriplets(nums=[4, 5, 6, 7, 8, 9], difference=2))

