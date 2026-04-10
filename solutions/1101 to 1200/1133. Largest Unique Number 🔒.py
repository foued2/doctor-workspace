from typing import List


class Solution:
    @staticmethod
    def largestUniqueNumber(nums: List[int]) -> int:
        # Initialize a set to keep track of numbers and their uniqueness
        table = set()

        # Iterate through each number in the input list
        for num in nums:
            # If the number is already in the set, it's a duplicate, so remove it from the set
            if num in table:
                table.remove(num)
            else:
                # If the number is not in the set, add it to the set
                table.add(num)

        # If the set is not empty, convert it to a list, sort it, and return the last (largest) element
        if table:
            return sorted(table)[-1]  # Use sorted to ensure we get the largest element
        else:
            # If the set is empty, return -1 indicating no unique number exists
            return -1


# Example usage
solution = Solution()
print(solution.largestUniqueNumber([5, 7, 3, 9, 4, 9, 8, 3, 1]))  # Output: 8
print(solution.largestUniqueNumber([9, 9, 8, 8]))  # Output: -1
print(solution.largestUniqueNumber([4, 10, 3, 3, 2, 4]))  # Output: 10
