class Solution:
    @staticmethod
    def numSteps(s: str) -> int:
        ans = 0  # Initialize the step counter

        # Continue the loop until the binary string is reduced to '1'
        while s != '1':
            if s[-1] == '0':
                # If the last character is '0', perform a right shift
                # This is equivalent to integer division by 2
                s = bin(int(s, 2) >> 1)[2:]
            else:
                # If the last character is '1', add 1 to the number
                # This is equivalent to incrementing the binary number, which may involve carrying
                s = bin(int(s, 2) + 1)[2:]
            # Increase the step counter after each operation
            ans += 1

        return ans  # Return the total number of steps taken


if __name__ == "__main__":
    # Example usage of the function to determine the number of steps to reduce the binary string to '1'
    print(Solution().numSteps(s="1101"))  # Outputs the minimum steps to reduce '1101' to '1'