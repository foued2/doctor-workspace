class Solution:
    @staticmethod
    def reverseBits(n: int) -> int:
        """
        Bit manipulation
        """
        result = 0  # This will store the reversed bits.
        for _ in range(32):
            # Left-shift the result by 1 bit to make space for the next bit.
            result = (result << 1)

            # Use bitwise AND with 1 to get the least significant bit of n,
            # and OR it with result to add this bit to the reversed result.
            result = result | (n & 1)

            # Right-shift n by 1 bit to process the next bit.
            n >>= 1

        return result  # After the loop, result contains the reversed bits.


if __name__ == "__main__":
    # Example usage: reversing the bits of the number 43261596
    print(Solution().reverseBits(n=43261596))