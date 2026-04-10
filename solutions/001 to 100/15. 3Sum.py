from typing import List, Tuple  # Importing the List class from the typing module.


class Solution:  # Creating a class named Solution
    @staticmethod  # Using a decorator to denote the method as a static method
    def threeSum(nums: List[int]) -> list[tuple[int, int, int]]:
        # Defining a method named threeSum that takes in a list of integers and returns a list of integers.
        target = 0  # Setting the target sum to 0
        nums.sort()  # Sorting the input list in ascending order

        s = set()  # Creating an empty set to store the unique triplets

        for i in range(len(nums)):  # For each number in the input list
            j = i + 1  # Initialize j to the next index
            k = len(nums) - 1  # Initialize k to the last index of the list

            while j < k:  # While j is less than k
                sum = nums[i] + nums[j] + nums[k]  # Calculate the sum of the three numbers
                if sum == target:
                    # If the sum is equal to the target (0), add the triplet to the set and move both j and k
                    s.add((nums[i], nums[j], nums[k]))
                    j += 1
                    k -= 1
                elif sum < target:
                    # If the sum is less than the target, increment j to adjust the sum
                    j += 1
                else:
                    # If the sum is greater than target, decrement k to adjust the sum
                    k -= 1

        output = list(s)  # Convert the set into a list

        return output  # Return the list of triplets

    print(threeSum([-1, 0, 1, 2, -1, -4]))  # Test the function with a custom list
