class Solution:
    @staticmethod
    def fib(n: int) -> int:
        """
        Dynamic programming
        Tabulation
        """
        # Base cases for a Fibonacci sequence
        if n == 0:
            return 0
        if n == 1:
            return 1

        # Initialize variables to store Fibonacci sequence
        fib_sequence = [0, 1]  # Starting with the first two elements

        # Loop to generate a Fibonacci sequence up to the nth element
        for i in range(2, n + 1):
            # Calculate the next Fibonacci number by adding the last two numbers
            next_fib = fib_sequence[-1] + fib_sequence[-2]
            fib_sequence.append(next_fib)

        # Return the nth Fibonacci number
        return fib_sequence[n]


if __name__ == '__main__':
    # Call the correct method name, `fib`, instead of `fibo`
    print(Solution.fib(20577))
