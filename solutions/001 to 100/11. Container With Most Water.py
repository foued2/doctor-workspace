# MEDIUM // ARRAY // TWO POINTERS (First, Last) // GREEDY (Max Value)

# We import 'List' from 'typing' to use as a type hint in function parameters
from typing import List


# We define a class named 'Solution'. This class contains the function we want to define
class Solution:

    # We define 'maxArea' as a static method. Static methods belong to the class, not instances of the class
    @staticmethod
    # 'maxArea' function takes a List of integers named 'height' as argument and return an integer
    def maxArea(height: List[int]) -> int:

        # We initialize 'max_c' (which probably stands for maximum capacity) to 0
        max_c = 0

        # 'j' is initially the index of the last item
        j = len(height) - 1

        # 'i' is initially the index of the first item
        i = 0

        # We enter a loop that continues as long as 'i' is less than 'j'
        while i < j:

            # If the value at position 'i' in height is less than or equal to the value at position 'j'...
            if height[i] <= height[j]:
                # We calculate the current capacity ('c') by multiplying the smaller value by the distance between
                # 'i' and 'j'
                c = height[i] * (j - i)

                # We increase 'i' by one
                i += 1
            # If the value at position 'i' in height is greater than the value at position 'j'...
            else:
                # We calculate the current capacity ('c') by multiplying the smaller value by the distance between
                # 'i' and 'j'
                c = height[j] * (j - i)

                # We decrease 'j' by one
                j -= 1

            # if max_c is less or equal to c, assign c to max_c 
            if max_c <= c:
                max_c = c

        # After we've gone through all pairs of height indices, 'max_c' should contain the maximum capacity. So we
        # return it
        return max_c

    # The function 'maxArea' is invoked with argument [1, 1], and the result is printed
    print(maxArea([1, 1, 5, 5]))
