from typing import List


class Solution:
    @staticmethod
    def countCompleteDayPairs(hours: List[int]) -> int:
        # Initialize the result count
        res = 0

        # Create an array to keep track of frequencies of hours % 24
        count = [0] * 24

        # Iterate through each hour in the list
        for hour in hours:
            # Calculate the complement needed to form a complete day (24 hours)
            complement = (24 - hour % 24) % 24

            # Add the count of the complement to the result
            # This represents how many valid pairs can be made with the current hour
            res += count[complement]

            # Increment the frequency count for the current hour % 24
            count[hour % 24] += 1

        # Return the total number of valid pairs
        return res


if __name__ == "__main__":
    # Test cases to verify the implementation
    print(Solution.countCompleteDayPairs([12, 12, 30, 24, 24]))  # Expected Output: 3 ([12, 12], [24, 24], [30, 24])
    print(Solution.countCompleteDayPairs([72, 48, 24, 3]))  # Expected Output: 3 ([72, 24], [48, 24], [24, 24])
    print(Solution.countCompleteDayPairs([3, 21, 9, 15, 12]))  # Expected Output: 1 ([3, 21])
    print(Solution.countCompleteDayPairs([5, 19, 13, 11]))  # Expected Output: 2 ([5, 19], [13, 11])