class Solution:
    @staticmethod
    def reverse(x: int) -> int:
        # Convert x to a string
        x_str = str(x)

        # Reverse the string representation of x
        reversed_str = x_str[::-1]

        # Remove the negative sign if present
        if x < 0:
            reversed_str = reversed_str[:-1]
            reversed_int = int(reversed_str) * -1
            if reversed_int <= -2147483648:
                return 0
        else:
            reversed_int = int(reversed_str)
            if reversed_int >= 2147483647:
                return 0

        # Assign the result back to x
        x = reversed_int
        return x


if __name__ == '__main__':
    print(Solution.reverse(0))
