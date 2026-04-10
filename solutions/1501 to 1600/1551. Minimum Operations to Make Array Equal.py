class Solution:
    @staticmethod
    def minOperations(n: int) -> int:
        # Initialize the answer to 0
        ans = 0

        # The line below generates the array, but it's commented out since it's not needed for the calculation
        # nums = [(2 * i) + 1 for i in range(n)]
        # print(nums)

        # Loop through the first half of the array
        for i in range(n // 2):
            # Add the value of the current element in the first half to the answer
            ans += (2 * i) + 1

        # If n is odd, add the middle element to the answer
        if n % 2 != 0:
            ans += n // 2

        # Return the total number of operations
        return ans


print(Solution.minOperations(n=100))
