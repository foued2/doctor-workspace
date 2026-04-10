class Solution:
    @staticmethod
    def hammingWeight(n: int) -> int:
        # Initialize the count of '1' bits to zero
        count = 0

        # Iterate as long as n is not zero
        while n:
            # Perform bitwise AND between n and (n-1)
            # This operation removes the lowest set bit from n
            # print(n, '&', n - 1, '=', n & (n - 1))
            n &= n - 1

            # Increment the count of '1' bits
            count += 1

        # Return the total count of '1' bits
        return count


if __name__ == "__main__":
    # Example usage: prints the number of '1' bits in the binary representation of 11
    print(Solution().hammingWeight(n=11))


class Solution:
    @staticmethod
    def hammingWeight(n: int) -> int:
        # Utilize the bit_count() method to count the number of '1' bits in n
        return n.bit_count()


if __name__ == "__main__":
    # Example usage: prints the number of '1' bits in the binary representation of 11
    print(Solution().hammingWeight(n=11))