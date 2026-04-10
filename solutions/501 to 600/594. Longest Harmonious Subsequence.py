from typing import List


class Solution:
    @staticmethod
    def findLHS(nums: List[int]) -> int:
        # Get the length of the input list
        n = len(nums)

        # If there's only one element in the list, return 0 as per problem requirements
        if n == 1:
            return 0

        # Create a dictionary to count the frequency of each number
        num_counts = {}
        for num in nums:
            num_counts[num] = num_counts.get(num, 0) + 1

        # Initialize a variable to track the largest possible length
        largest = 0

        # Loop through the unique numbers in the dictionary
        for num in num_counts:
            # Check if the next number exists in the dictionary and its absolute difference is 1
            if num + 1 in num_counts:
                # Update the largest length if the sum of counts is larger
                largest = max(largest, num_counts[num] + num_counts[num + 1])

        # Return the largest length found
        return largest


if __name__ == '__main__':
    print(Solution.findLHS(nums=[1, 3, 2, 9, 5, 3, 7]))
    print(Solution.findLHS(nums=[1, 2, 3, 4]))
    print(Solution.findLHS(nums=[1, 1, -1, 1]))
    print(Solution.findLHS(nums=[1, 2, 2, 1]))
    print(Solution.findLHS(nums=[1, 5]))
    print(Solution.findLHS([-1, 0, -1, 0, -1, 0, -1]))
