from typing import List


class Solution:
    @staticmethod
    def sumIndicesWithKSetBits(nums: List[int], k: int) -> int:
        """
        Bit manipulation
        """
        # Get the length of the input list
        length = len(nums)
        # Initialize the result variable to store the sum of elements
        total_sum = 0
        # Iterate over each index in the list
        for index in range(length):
            current_index = index
            # Initialize count to keep track of the number of set bits
            set_bits_count = 0
            # Count the number of set bits in the binary representation of current_index
            while current_index:
                # Add 1 to set_bits_count if the least significant bit of current_index is 1
                set_bits_count += current_index & 1
                # Right shift current_index by 1 to check the next bit
                current_index >>= 1
            # If the number of set bits is equal to k
            if set_bits_count == k:
                # Add the element at the current index to the total_sum
                total_sum += nums[index]
        # Return the total sum
        return total_sum


print(Solution.sumIndicesWithKSetBits(nums=[5, 10, 1, 5, 2], k=1))
