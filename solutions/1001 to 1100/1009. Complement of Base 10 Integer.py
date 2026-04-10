class Solution:
    @staticmethod
    def bitwiseComplement(n: int) -> int:
        """
        Bit manipulation
        """
        # Calculate the number of bits required
        num_bits = len(bin(n)) - 2
        # Invert the bits and mask with the appropriate number of bits
        result = ~n & ((1 << num_bits) - 1)
        return result


print(Solution.bitwiseComplement(5))


class Solution:
    @staticmethod
    def bitwiseComplement(n: int) -> int:
        """
        Bit-masking
        """
        # If n is 0 or 1, return the bitwise complement directly
        if n < 2:
            return int(not n)

        mask = n
        shift = 1

        # Iterate until mask becomes pow2(n) - 1
        while (mask + 1) & mask:  # mask != pow2(n) - 1
            # Expand the mask by setting additional bits to 1
            mask |= mask >> shift
            # Double the shift value for the next iteration
            shift <<= 1

        # Return the bitwise XOR of n and the mask to get the complement
        return n ^ mask
