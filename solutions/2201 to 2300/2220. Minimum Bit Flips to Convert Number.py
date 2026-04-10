class Solution:
    @staticmethod
    def minBitFlips(start: int, goal: int) -> int:
        # Calculate the XOR of start and goal.
        # The XOR operation highlights the positions where the bits differ.
        xor = goal ^ start

        # Use the bit_count() method to count the number of 1s in the binary representation of xor.
        # Each 1 represents a differing bit that needs to be flipped.
        ans = xor.bit_count()

        # Return the count of differing bits, which is the minimum number of flips required.
        return ans


print(Solution.minBitFlips(start=3, goal=4))
