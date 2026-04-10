class Solution:
    @staticmethod
    def pivotInteger(n: int) -> int:
        """
        Prefix sum, pivot
        """
        # Calculate the total sum of numbers from 1 to n
        total_sum = (n * (n + 1)) // 2

        # Initialize the left sum
        left_sum = 0

        # Iterate through the numbers from 1 to n
        for num in range(1, n + 1):
            # Calculate the current right sum by subtracting the left sum and current number from the total sum
            right_sum = total_sum - left_sum - num

            # Check if the left sum equals the right sum
            if left_sum == right_sum:
                return num

            # Add the current number to the left sum
            left_sum += num

        # If no pivot integer is found, return -1
        return -1


# Test cases
print(Solution.pivotInteger(5))  # Expected output: -1 (no pivot exists)
print(Solution.pivotInteger(8))  # Expected output: 6 (left sum = 21, right sum = 21)

