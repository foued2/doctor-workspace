class Solution:
    @staticmethod
    def countSymmetricIntegers(low: int, high: int) -> int:
        # Helper function to check if a number is symmetric
        def is_symmetric(num: int) -> bool:
            digits = list(map(int, str(num)))
            length = len(digits)
            half_length = length // 2
            # Check if the sum of the first half digits equals the sum of the second half digits
            return sum(digits[:half_length]) == sum(digits[half_length:])

        # Initialize the count of symmetric integers
        symmetric_count = 0

        # Handle two-digit symmetric numbers (11, 22, ..., 99)
        for num in range(11, 100, 11):
            if low <= num <= high:
                symmetric_count += 1

        # Handle four-digit symmetric numbers
        for num in range(max(1000, low), min(high + 1, 10000)):
            if is_symmetric(num):
                symmetric_count += 1

        return symmetric_count


# Example usage:
solution = Solution()
result = solution.countSymmetricIntegers(10, 1234)
print(result)  # Example output: count of symmetric integers within the range
