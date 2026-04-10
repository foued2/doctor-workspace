from typing import List


class Solution:
    @staticmethod
    def maximumSumOfHeights(heights: List[int]) -> int:
        """
        Stack solution
        """
        n = len(heights)

        # Arrays to store cumulative sums for non-decreasing sequences
        left = [0] * n
        right = [0] * n

        # Stack to maintain non-decreasing order for left processing
        stack = []
        for i in range(n):
            # Maintain non-decreasing sequence in stack
            while stack and heights[stack[-1]] >= heights[i]:
                stack.pop()

            # Calculate left[i] based on previous elements
            if stack:
                left[i] = left[stack[-1]] + (i - stack[-1]) * heights[i]
            else:
                left[i] = (i + 1) * heights[i]

            # Push current index into the stack
            stack.append(i)

        # Clear the stack to reuse for right processing
        stack = []
        for i in range(n - 1, -1, -1):
            # Maintain non-decreasing sequence in stack
            while stack and heights[stack[-1]] >= heights[i]:
                stack.pop()

            # Calculate right[i] based on subsequent elements
            if stack:
                right[i] = right[stack[-1]] + (stack[-1] - i) * heights[i]
            else:
                right[i] = (n - i) * heights[i]

            # Push current index into the stack
            stack.append(i)

        # Calculate maximum sum combining both sides while avoiding double counting the peak
        max_sum = 0
        for i in range(n):
            max_sum = max(max_sum, left[i] + right[i] - heights[i])

        return max_sum


# Test the case provided by the user
if __name__ == '__main__':
    print(Solution().maximumSumOfHeights(heights=[2, 4, 5, 2, 5, 5, 2, 1, 1, 3]))  # Should output 23
