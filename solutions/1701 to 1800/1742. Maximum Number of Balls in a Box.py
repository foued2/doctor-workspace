class Solution:
    @staticmethod
    def countBalls(lowLimit: int, highLimit: int) -> int:
        # Initialize the maximum count of balls in any box to 0
        ans = 0

        # Initialize a dictionary to keep track of the number of balls in each box
        table = {}

        # Iterate over the range from lowLimit to highLimit (inclusive)
        for num in range(lowLimit, highLimit + 1):
            # Initialize the sum of digits for the current number
            sum_num = 0

            # Make a copy of the current number to calculate the digit sum
            current = num

            # Calculate the sum of digits of the current number
            while current:
                # Add the last digit of current to sum_num
                sum_num += current % 10
                # Remove the last digit from current
                current //= 10

            # Update the count of balls in the box corresponding to sum_num
            table[sum_num] = table.get(sum_num, 0) + 1

            # Update the maximum count if the current box has more balls
            if table[sum_num] > ans:
                ans = table[sum_num]

        # Return the maximum count of balls in any box
        return ans


print(Solution.countBalls(lowLimit=19, highLimit=28))
