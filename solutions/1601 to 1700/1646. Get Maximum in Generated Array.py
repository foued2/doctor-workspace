class Solution:
    @staticmethod
    def getMaximumGenerated(n: int) -> int:
        # Handle the special case where n is 0
        if n == 0:
            return 0

        # Create a list of size n+1 filled with zeros to store generated elements
        nums = [0] * (n + 1)

        # Set base case values, only set nums[1] if n >= 1
        if n >= 1:
            nums[1] = 1

        # Loop counter to iterate through generations
        i = 1

        # Loop as long as the index of the element to be generated is within range
        while (2 * i + 1) <= n:
            # Left child gets the value from the first parent
            nums[2 * i] = nums[i]
            # The right child gets the sum of both parents
            nums[2 * i + 1] = nums[i] + nums[i + 1]
            # Increment loop counter for the next generation
            i += 1

        # Return the maximum value in the list (maximum generated element)
        return max(nums)


# Example usage:
print(Solution.getMaximumGenerated(0))  # Output should be 0
print(Solution.getMaximumGenerated(7))  # Output should be the maximum value in the generated list

print(Solution.getMaximumGenerated(n=1))
