from typing import List


class Solution:
    @staticmethod
    def countDistinctIntegers(nums: List[int]) -> int:
        # Initialize a set with the original list of numbers to store distinct integers
        distinct_integers = set(nums)
        # Initialize a new set to temporarily store the reversed numbers
        new_elements = set()

        # Iterate over each number in the original set of distinct integers
        for num in distinct_integers:
            # Reverse the number by converting it to a string, reversing the string,
            # and converting it back to an integer
            reversed_num = int(str(num)[::-1])
            # Add the reversed number to the set of new elements
            new_elements.add(reversed_num)

        # Update the original set with the new elements collected
        distinct_integers.update(new_elements)

        # The number of distinct integers is the size of the updated set
        ans = len(distinct_integers)

        # Return the number of distinct integers
        return ans


# Example usage
print(Solution.countDistinctIntegers(nums=[123, 321, 456, 654]))  # Output example
