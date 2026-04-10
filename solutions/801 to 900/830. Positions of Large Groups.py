from typing import List


class Solution:
    @staticmethod
    def largeGroupPositions(s: str) -> List[List[int]]:
        # Initialize the count of consecutive characters and the previous character tracker
        count, prev, intervals = 1, None, []

        # Add a sentinel character to the end of the string to handle the final group
        s += "!"

        # Iterate through the string with index and character
        for i, ch in enumerate(s):
            # If the current character is different from the previous one
            if ch != prev:
                # Check if the previous group has 3 or more characters
                if count >= 3:
                    # Add the start and end indices of the large group to intervals
                    intervals.append([i - count, i - 1])
                # Reset the count for the new character
                count = 1
            else:
                # Increment the count for the same consecutive character
                count += 1
            # Update the previous character to the current one
            prev = ch

        # Return the list of intervals for large groups
        return intervals


# Example usage
solution = Solution()
print(solution.largeGroupPositions("abbxxxxzzy"))  # Expected output: [[3, 6]]
