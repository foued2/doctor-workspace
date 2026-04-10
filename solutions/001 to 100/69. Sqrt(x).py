class Solution:
    @staticmethod
    def mySqrt(x: int) -> int:
        # Edge case: Return 0 if x is 0
        if x == 0:
            return 0

        # Initialize left and right pointers for binary search
        left, right = 1, x

        # Binary search loop
        while left <= right:
            # Calculate the mid-index using integer division
            mid = left + (right - left) // 2

            # Check if the square of mid is equal to x
            if mid * mid == x:
                return mid
            # If the square of mid is less than x, search the right half
            elif mid * mid < x:
                left = mid + 1
            # If the square of mid is greater than x, search the left half
            else:
                right = mid - 1

        # Return the integer part of the square root of x
        return right


# Test the function
if __name__ == '__main__':
    print(Solution.mySqrt(10))  # Output: 3
