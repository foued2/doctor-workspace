from typing import List


class Solution:
    @staticmethod
    def isArraySpecial(nums: List[int]) -> bool:
        # Helper function to determine the parity of a number
        def Parity(num: int) -> str:
            # Check if the number is even
            if num % 2 == 0:
                return 'Even'  # Return 'Even' if the number is divisible by 2
            else:
                return 'Odd'  # Return 'Odd' if the number is not divisible by 2

        # Get the length of the input list
        n = len(nums)

        # Iterate through the list up to the second last element
        for i in range(0, n - 1):
            # Compare the parity of the current element with the next element
            if Parity(nums[i]) == Parity(nums[i + 1]):
                return False  # If two consecutive elements have the same parity, return False

        return True  # If no consecutive elements have the same parity, return True


# Example usage
solution = Solution()
print(solution.isArraySpecial([1, 2, 3, 4]))  # Expected output: True


class Solution:
    @staticmethod
    def isArraySpecial(nums: List[int]) -> bool:
        """
        Bit manipulation
        """
        # Determine if the first element is odd (1) or even (0) using bitwise AND
        isOdd = nums[0] & 1

        # Iterate through the list starting from the second element
        for num in nums[1:]:
            # Check if the current number has the same odd/even parity as expected
            if (num & 1) == isOdd:
                return False  # If it matches the expected parity, return False
            # Toggle the expected parity for the next iteration
            isOdd ^= 1

        # If all numbers alternate as expected, return True
        return True


# Example usage
solution = Solution()
print(solution.isArraySpecial([1, 2, 3, 4]))  # Expected output: True
print(solution.isArraySpecial([2, 4, 6, 8]))  # Expected output: False
print(solution.isArraySpecial([1, 3, 5, 7]))  # Expected output: False
print(solution.isArraySpecial([1, 2, 2, 3]))  # Expected output: False
print(solution.isArraySpecial([1, 2, 1, 2]))  # Expected output: True
