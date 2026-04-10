from typing import List


class Solution:
    @staticmethod
    def evenOddBit(n: int) -> List[int]:
        # Initialize counters for even and odd positions
        even, odd = 0, 0
        # Initialize parity to track the position (True for even, False for odd)
        parity = True  # True = even, False = odd

        # Loop until all bits are processed
        while n:
            # Check if the least significant bit is 1
            if n & 1:
                # Increment the appropriate counter based on the parity
                if parity:
                    even += 1
                else:
                    odd += 1
            # Right shift the number by 1 bit to process the next bit
            n >>= 1
            # Toggle the parity for the next bit
            parity = not parity

        # Return the counts of bits set to 1 at even and odd positions
        return [even, odd]


# Test cases
print(Solution().evenOddBit(2))  # Output should be [1, 0]
print(Solution().evenOddBit(3))  # Output should be [1, 1]
print(Solution().evenOddBit(10))  # Output should be [1, 1]
