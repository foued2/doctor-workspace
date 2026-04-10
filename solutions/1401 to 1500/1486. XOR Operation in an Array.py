class Solution:
    @staticmethod
    def xorOperation(n: int, start: int) -> int:
        # Step 1: Generate the sequence of numbers
        nums = [start + (2 * i) for i in range(n)]

        # Initialize the result with the starting value
        ans = start

        # Step 2: Perform XOR operation on all elements in the sequence
        for num in nums[1:]:
            ans ^= num

        # Step 3: Return the final result
        return ans


print(Solution.xorOperation(n=4, start=3))
