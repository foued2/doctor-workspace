class Solution:
    @staticmethod
    def numberOfSteps(num: int) -> int:
        count = 0  # Initialize a counter to keep track of the number of steps

        # Continue the loop until 'num' becomes zero
        while num != 0:
            # If 'num' is even, divide it by 2
            if num % 2 == 0:
                num //= 2
            # If 'num' is odd, subtract 1 from it
            else:
                num -= 1

            # Increment the step count
            count += 1

        # Return the total number of steps required
        return count


if __name__ == '__main__':
    print(Solution.numberOfSteps(14))

