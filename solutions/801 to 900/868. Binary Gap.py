class Solution:
    @staticmethod
    def binaryGap(n: int) -> int:
        """
        Bit manipulation
        """
        # Initialize the maximum distance found to 0
        ans = 0
        # Initialize the position of the previous '1' bit to -1 indicating no '1' found yet
        prev = -1
        # Initialize the position counter
        pos = 0

        # Loop through each bit of the number
        while n > 0:
            # Check if the current bit is '1'
            if (n & 1) == 1:
                # If there was a previous '1', calculate the distance to the current '1'
                if prev != -1:
                    distance = pos - prev
                    # Update the maximum distance found
                    ans = max(distance, ans)
                # Update the position of the previous '1' to the current position
                prev = pos
            # Right shift the number by 1 to check the next bit
            n >>= 1
            # Increment the position counter
            pos += 1

        # Return the maximum distance found
        return ans


# Example usage
print(Solution.binaryGap(22))  # Output should be 2, as binary representation of 22 is '10110'
