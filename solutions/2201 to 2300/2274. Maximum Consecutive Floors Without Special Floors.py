from typing import List


class Solution:
    @staticmethod
    def maxConsecutive(bottom: int, top: int, special: List[int]) -> int:
        # Initialize the answer to store the maximum consecutive floors count
        ans = 0

        # Start from the bottom floor
        floor = bottom

        # Initialize current consecutive count
        curr = 0

        # Iterate from the bottom to the top floor
        while floor <= top:
            if floor not in special:
                # If the floor is not special, increment the current consecutive count
                curr += 1
            else:
                # If the floor is special, reset the current consecutive count
                curr = 0

            # Move to the next floor
            floor += 1

            # Update the maximum consecutive count
            ans = max(ans, curr)

        return ans


# Example Usage
bottom = 2
top = 9
special = [4, 6]

# Create an instance of Solution and call the maxConsecutive method
solution = Solution()
result = solution.maxConsecutive(bottom, top, special)

# Print the result
print(result)  # Output: 3

print(Solution.maxConsecutive(bottom=2, top=9, special=[4, 6]))


class Solution:
    @staticmethod
    def maxConsecutive(bottom: int, top: int, special: List[int]) -> int:
        # Sort the special floors to ensure they are in order
        special.sort()

        # Initialize the maximum gap as the distance between the bottom and the first special floor
        max_gap = special[0] - bottom

        # Iterate through the sorted special floors to find the maximum gap between consecutive special floors
        for i in range(1, len(special)):
            max_gap = max(max_gap, special[i] - special[i - 1] - 1)

        # Consider the gap between the last special floor and the top
        max_gap = max(max_gap, top - special[-1])

        return max_gap


# Example Usage
bottom = 2
top = 9
special = [4, 6]

# Create an instance of Solution and call the maxConsecutive method
solution = Solution()
result = solution.maxConsecutive(bottom, top, special)

# Print the result
print(result)  # Output: 3
