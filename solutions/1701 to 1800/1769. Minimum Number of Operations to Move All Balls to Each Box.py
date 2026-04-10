from typing import List


class Solution:
    @staticmethod
    def minOperations(boxes: str) -> List[int]:
        n = len(boxes)
        # Initialize the result list with zeros
        res = [0] * n

        # Two passes approach: one from left to right and one from right to left

        # First pass: left to right
        left_sum = 0  # To keep the sum of all ball indices on the left side
        count = 0  # To keep the count of balls on the left side

        for i in range(n):
            # Add the current count of balls to the result for the current position
            res[i] += left_sum
            # If the current box has a ball, update count
            if boxes[i] == '1':
                count += 1
            # Update left_sum to reflect the cost of moving balls to the next position
            left_sum += count

        # Second pass: right to left
        right_sum = 0  # To keep the sum of all ball indices on the right side
        count = 0  # To keep the count of balls on the right side

        for i in range(n - 1, -1, -1):
            # Add the current count of balls to the result for the current position
            res[i] += right_sum
            # If the current box has a ball, update count
            if boxes[i] == '1':
                count += 1
            # Update right_sum to reflect the cost of moving balls to the previous position
            right_sum += count

        return res


# Example usage:
boxes = "110"
solution = Solution()
print(solution.minOperations(boxes))  # Output: [1, 1, 3]

print(Solution.minOperations(boxes="001011"))  # [11,8,5,4,3,4]
