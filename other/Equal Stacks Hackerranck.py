#
# Complete the 'equalStacks' function below.
#
# The function is expected to return an INTEGER.
# The function accepts the following parameters:
#  1. INTEGER_ARRAY h1
#  2. INTEGER_ARRAY h2
#  3. INTEGER_ARRAY h3
#

def equalStacks(h1, h2, h3):
    """
    Stack
    """
    # Calculate the total height of each stack
    total_h1 = sum(h1)
    total_h2 = sum(h2)
    total_h3 = sum(h3)

    # Iterate until the heights are equal
    while True:
        # Find the minimum height among the three stacks
        min_height = min(total_h1, total_h2, total_h3)

        # If all three stacks have the same height, return it
        if total_h1 == total_h2 == total_h3:
            return total_h1

        # Remove cylinders from the tallest stack until its height is <= min_height
        while total_h1 > min_height:
            total_h1 -= h1.pop(0)
        while total_h2 > min_height:
            total_h2 -= h2.pop(0)
        while total_h3 > min_height:
            total_h3 -= h3.pop(0)


# Example usage:
h1 = [3, 2, 1, 1, 1]
h2 = [4, 3, 2]
h3 = [1, 1, 4, 1]

print(equalStacks(h1, h2, h3))  # Output: 5
