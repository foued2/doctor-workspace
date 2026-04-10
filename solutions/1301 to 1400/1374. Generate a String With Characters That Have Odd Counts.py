class Solution:
    @staticmethod
    def generateTheString(n: int) -> str:
        # If 'n' is even
        if n % 2 == 0:
            # Return a string with 'n - 1' occurrences of 'a' followed by one occurrence of 'b'
            return ((n - 1) * 'a') + 'b'
        # If 'n' is odd
        else:
            # Return a string with 'n' occurrences of 'a'
            return 'a' * n


if __name__ == '__main__':
    print(Solution.generateTheString(7))