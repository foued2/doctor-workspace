from typing import List


class Solution:
    @staticmethod
    def categorizeBox(length: int, width: int, height: int, mass: int) -> str:
        # Calculate the volume of the box
        volume = length * width * height

        # Initialize an empty list to hold the description categories
        description = []

        # Check if any dimension is 10^4 or more, or if the volume is 10^9 or more
        if any(dim >= 10 ** 4 for dim in [length, width, height]) or volume >= 10 ** 9:
            # If true, the box is considered 'Bulky'
            description.append('Bulky')

        # Check if the mass is 100 or more
        if mass >= 100:
            # If true, the box is considered 'Heavy'
            description.append('Heavy')

        # Determine the category based on the descriptions in the list
        if description == ['Bulky', 'Heavy']:
            # If both conditions are met, the category is 'Both'
            category = 'Both'
        elif not description:
            # If neither condition is met, the category is 'Neither'
            category = 'Neither'
        elif description == ['Bulky']:
            # If only the bulky condition is met, the category is 'Bulky'
            category = 'Bulky'
        else:
            # If only the heavy condition is met, the category is 'Heavy'
            category = 'Heavy'

        # Return the final category
        return category


# Example usage:
length = 10000
width = 2000
height = 3000
mass = 150
solution = Solution()
print(solution.categorizeBox(length, width, height, mass))  # Output should be 'Both'
