from typing import List


class Solution:
    @staticmethod
    def getNoZeroIntegers(n: int) -> List[int]:
        # Initialize a and b; a will iterate from 1 to n-1, b is initially set to n
        a, b = 0, n

        # Iterate over possible values of a from 1 to n-1
        for i in range(1, n):
            # Assign the current value of i to a
            a = i
            # Compute b as the difference n - a
            b = n - i

            # Check if either a or b contains the digit '0'
            # Convert a and b to strings and check for '0' in the string representation
            if '0' in str(a) or '0' in str(b):
                # If either contains '0', continue to the next iteration
                continue

            # If both a and b do not contain '0', return them as the result
            return [a, b]


print(Solution.getNoZeroIntegers(n=11))
