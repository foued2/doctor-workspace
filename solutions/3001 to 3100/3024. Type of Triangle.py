from typing import List


class Solution:
    @staticmethod
    def triangleType(nums: List[int]) -> str:
        """
        Triangle Inequality Theorem:
        Concept: The sum of the lengths of any two sides of a triangle must be greater than
        the length of the remaining side.
        """
        # Check if the lengths of any two sides are greater than the length of the third side
        if nums[0] + nums[1] > nums[2] and nums[0] + nums[2] > nums[1] and nums[2] + nums[1] > nums[0]:
            # If valid, check the type of triangle based on the lengths of its sides
            if len(set(nums)) == 1:
                return "equilateral"  # All sides are of equal length
            elif len(set(nums)) == 2:
                return "isosceles"  # Two sides are of equal length
            else:
                return "scalene"  # No sides are of equal length
        else:
            return 'None'  # If not a valid triangle, return 'None'


if __name__ == '__main__':
    # Test the method with a sample input and print the result
    print(Solution.triangleType(nums=[1, 4, 3]))

