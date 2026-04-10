class Solution:
    @staticmethod
    def smallestEvenMultiple(n: int) -> int:
        # Initialize the result variable
        # res = 0

        # Check if the given number is even
        if n % 2 == 0:
            # If it's even, assign the result as the given number
            res = n
        else:
            # If it's odd, double the number and assign it as the result
            res = 2 * n

        # Return the result
        return res


if __name__ == '__main__':
    print(Solution.smallestEvenMultiple(n=6))
