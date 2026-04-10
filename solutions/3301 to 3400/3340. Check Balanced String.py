
# Define Solution class to contain methods
class Solution:

    # Decorator to declare a static method
    @staticmethod

    # Static method to check if the sum of digits at even positions
    # equals the sum at odd positions
    def isBalanced(num: str) -> bool:

        # Get the length of the input string
        n = len(num)

        # Index to start with even positions
        even = 0

        # Initialize sum of even-position digits
        sum_even = 0

        # Index to start with odd positions
        odd = 1

        # Initialize sum of odd-position digits
        sum_odd = 0

        # Iterate over even-position digits
        for i in range(even, n, 2):

            # Add digit at even position to sum_even
            sum_even += int(num[i])

        # Iterate over odd-position digits
        for i in range(odd, n, 2):

            # Add digit at odd position to sum_odd
            sum_odd += int(num[i])

        # Return True if sums are equal, otherwise False
        return sum_even == sum_odd


# Main block to test the function
if __name__ == "__main__":

    # Test the isBalanced method with a sample number
    print(Solution().isBalanced("1234"))
