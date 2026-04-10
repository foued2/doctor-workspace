from typing import List
from bisect import bisect_left, bisect_right


class Solution:
    @staticmethod
    def findSpecialInteger(arr: List[int]) -> int:
        """
        Binary search, majority element
        """
        def is_majority(candidate):
            # Find the range of indices where the candidate appears to use binary search
            left = bisect_left(arr, candidate)
            right = bisect_right(arr, candidate)
            # Check if the count of appearances is greater than a quarter of the array's length
            return (right - left) > len(arr) // 4

        # Iterate through the array to find possible candidates for the special integer
        for num in arr:
            # Check if the current number is a candidate for the special integer
            if is_majority(num):
                return num  # Return the candidate if it meets the condition

        return -1  # If no special integer is found, return -1


# Example usage:
if __name__ == "__main__":
    # Initialize the solution object
    solution = Solution()

    # Example array
    arr = [1, 2, 2, 6, 6, 6, 6, 7, 8, 9, 9, 9, 9]

    # Find the special integer
    special_integer = solution.findSpecialInteger(arr)

    # Print the result
    print("Special Integer:", special_integer)


class Solution:
    @staticmethod
    def findSpecialInteger(arr: List[int]) -> int:
        """
        Hash table
        """
        n = len(arr)
        if n == 1:
            return arr[0]

        # Calculate the threshold count
        threshold = n // 4

        # Initialize a dictionary to count occurrences of each element
        count_dict = {}

        # Iterate over the array and count occurrences of each element
        for num in arr:
            count_dict[num] = count_dict.get(num, 0) + 1
            if count_dict[num] > threshold:
                return num
