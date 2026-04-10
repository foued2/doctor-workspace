from typing import List


class Solution:
    @staticmethod
    def nextGreatestLetter(letters: List[str], target: str) -> str:
        # Convert letters to ASCII values
        nums = [ord(s) for s in letters]
        num = ord(target)

        # Initialize left and right pointers for binary search
        left, right = 0, len(nums) - 1

        # Binary search loop
        while left <= right:
            # Calculate the mid-index
            mid = (left + right) // 2

            # Check if the target is between nums[mid] and nums[mid + 1]
            if nums[mid] <= num < nums[(mid + 1) % len(nums)]:
                return letters[(mid + 1) % len(nums)]  # Wrap around if mid + 1 exceeds the length of letters
            # If the target is greater than or equal to nums[mid], search the right half
            elif nums[mid] <= num:
                left = mid + 1
            # If the target is smaller than nums[mid], search the left half
            else:
                right = mid - 1

        # Return the first letter if the target is greater than all letters
        return letters[0]


# Test the function
if __name__ == '__main__':
    print(Solution.nextGreatestLetter(letters=["c", "f", "j"], target="d"))  # Output: "f"
