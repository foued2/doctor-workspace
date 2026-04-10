from typing import List


class Solution:
    @staticmethod
    def finalPrices(prices: List[int]) -> List[int]:
        """
        Stack, Monotonic stack, unordered case
        """
        # Initialize an empty stack to keep track of indices of the elements
        stack = []

        # Iterate through each element in the array
        for i in range(len(prices)):
            # While the stack is not empty, and the current element is less than or equal to
            # the element corresponding to the index at the top of the stack
            while stack and prices[i] <= prices[stack[-1]]:
                # Pop the index from the stack
                idx = stack.pop()
                # The current element is the discount for the price at the popped index
                prices[idx] -= prices[i]

            # Push the current index onto the stack for future processing
            stack.append(i)

        # Return the modified prices array with discounts applied
        return prices


# Example usage:
solution = Solution()
print(solution.finalPrices([8, 4, 6, 2, 3]))  # Output: [4, 2, 4, 2, 3]
