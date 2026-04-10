class Solution:
    @staticmethod
    def addBinary(a: str, b: str) -> str:
        # Initialize integers to represent the binary string inputs
        x = int(a, 2)
        y = int(b, 2)

        # Iterate until there's no carry
        while y:
            # XOR operation to add bits where there is no carry
            sum_ = x ^ y
            # AND operation to find carry bits, then shift left by 1
            carry = (x & y) << 1
            # Update x and y for the next iteration
            x = sum_
            y = carry

        # Convert the final result back to a binary string and return it
        return bin(x)[2:]


if __name__ == "__main__":
    s = Solution()
    print(s.addBinary(a="11", b="1"))  # Output should be "100"