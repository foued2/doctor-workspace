class Solution:
    @staticmethod
    def maximumOddBinaryNumber(s: str) -> str:
        # Count the number of '1's and '0's in the string
        count_ones = s.count('1')
        count_zeros = len(s) - count_ones

        # Create the new binary string with the required structure
        max_odd_binary = '1' * (count_ones - 1) + '0' * count_zeros + '1'

        # Return the constructed binary string
        return max_odd_binary


# Example usage
s = "1101010"
print(Solution.maximumOddBinaryNumber(s))  # Output should be '1111001'

print(Solution.maximumOddBinaryNumber(s="001010111100001101101"))
